import time
import os
import argparse
import requests
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image  # For image compression

# API URL
API_URL = "https://api.twist.blue/v1/images?token=1231234"

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Capture images and send to a remote server.")
parser.add_argument("-i", type=int, default=10, help="Time between photos in seconds.")
parser.add_argument("-sd", type=str, default="~/camera_images", help="Local directory to save images.")
parser.add_argument("-q", type=int, default=50, help="Image quality, less is smaller file")

args = parser.parse_args()

# Expand user directory (if used)
save_dir = os.path.expanduser(args.sd)

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

# Ensure save directory exists
os.makedirs(save_dir, exist_ok=True)

def compress_image(filepath):
    """ Compress the captured image as a JPEG to reduce file size. """
    try:
        print(f"[INFO] Compressing {filepath} as JPEG...")
        img = Image.open(filepath)
        compressed_path = filepath.replace(".jpg", "_compressed.jpg")

        img.save(compressed_path, "JPEG", quality=args.q)  # Adjust quality (lower = smaller file)
        print(f"[SUCCESS] Compressed image saved: {compressed_path}")
        return compressed_path
    except Exception as e:
        print(f"[ERROR] Failed to compress image: {e}")
        return None

def capture_and_send():
    """ Captures an image, compresses it, and sends it to the API. """
    try:
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(save_dir, filename)

        # Capture Image
        print(f"[INFO] Capturing image: {filepath}")
        picam2.capture_file(filepath)
        print(f"[SUCCESS] Image captured: {filepath}")

        # Compress JPEG
        compressed_filepath = compress_image(filepath)
        if not compressed_filepath:
            print("[ERROR] Skipping upload due to compression failure.")
            return

        # Check file size before sending
        file_size = os.path.getsize(compressed_filepath) / 1024  # Convert to KB
        print(f"[INFO] File size after compression: {file_size:.2f} KB")

        # Send to API
        with open(compressed_filepath, "rb") as img_file:
            files = {"fileToUpload": (os.path.basename(compressed_filepath), img_file, "image/jpeg")}
            print(f"[INFO] Uploading {compressed_filepath} to {API_URL}...")
            response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            print(f"[SUCCESS] Upload complete! Server response: {response.text}")
        else:
            print(f"[ERROR] Upload failed. HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

# Main loop with KeyboardInterrupt handling
try:
    while True:
        capture_and_send()
        print(f"[INFO] Waiting for {args.i} seconds before next capture...\n")
        time.sleep(args.i)
except KeyboardInterrupt:
    print("\n[INFO] Script interrupted. Exiting cleanly...")