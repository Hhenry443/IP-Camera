import os
import time
import argparse
import requests
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Capture images and send to the sign-checker API.")
parser.add_argument("-i",  type=int, default=10,               help="Seconds between captures (default: 10).")
parser.add_argument("-sd", type=str, default="~/camera_images", help="Local directory to save images.")
parser.add_argument("-q",  type=int, default=50,               help="JPEG quality 1-95 (default: 50).")
parser.add_argument("-u",  type=str, required=True,            help="Correct URL encoded in this sign's QR code.")
parser.add_argument("-a",  type=str, required=True,            help="API endpoint, e.g. https://api.twist.blue/v1/images?token=xxx&type=images")
args = parser.parse_args()

save_dir = os.path.expanduser(args.sd)
os.makedirs(save_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def capture_image():
    """Capture a still from the camera and return its filepath."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(save_dir, f"{timestamp}.jpg")
    picam2.capture_file(filepath)
    print(f"[CAMERA] Captured {filepath}")
    return filepath


def compress_image(filepath):
    """Re-save the image as a compressed JPEG in place. Returns filepath or None on failure."""
    try:
        img = Image.open(filepath)
        img.save(filepath, "JPEG", quality=args.q)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"[COMPRESS] {size_kb:.1f} KB after compression (quality={args.q})")
        return filepath
    except Exception as e:
        print(f"[ERROR] Compression failed: {e}")
        return None


def send_image(filepath):
    """Send the image to the API and return the response, or None on failure."""
    try:
        with open(filepath, "rb") as f:
            response = requests.post(
                args.a,
                files={"fileToUpload": (os.path.basename(filepath), f, "image/jpeg")},
                data={"correct_url": args.u},
                timeout=130,  # Slightly above the Flask/Gunicorn timeout
            )
        return response
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None


def capture_and_send():
    """Full pipeline: capture → compress → send."""
    filepath = capture_image()

    filepath = compress_image(filepath)
    if filepath is None:
        return

    response = send_image(filepath)
    if response is None:
        return

    if response.status_code == 200:
        data = response.json()
        verdict = data.get("data", {}).get("verdict", "?")
        reason  = data.get("data", {}).get("reason", "")
        print(f"[API] {verdict} — {reason}")
    else:
        print(f"[API] Error {response.status_code}: {response.text}")

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

print(f"[INFO] Starting. Capturing every {args.i}s. Sign URL: {args.u}")

try:
    while True:
        capture_and_send()
        print(f"[INFO] Waiting {args.i}s...\n")
        time.sleep(args.i)
except KeyboardInterrupt:
    print("\n[INFO] Stopped.")
