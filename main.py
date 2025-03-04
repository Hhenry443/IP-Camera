import time
import os
import argparse
from datetime import datetime
from picamera2 import Picamera2

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Capture images and send to a remote Mac.")
parser.add_argument("-i", type=int, default=10, help="Time between photos in seconds.")
parser.add_argument("-sd", type=str, default="/path/to/camera_images", help="Local directory to save images.")
parser.add_argument("-ma", type=str, default="user@ip", help="Mac address for SCP transfer.")
parser.add_argument("-rd", type=str, default="~/received_images/", help="Remote directory on Mac.")

args = parser.parse_args()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

# Ensure save directory exists
os.makedirs(args.sd, exist_ok=True)

def capture_and_send():
    try:
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(args.sd, filename)

        # Capture image
        picam2.capture_file(filepath)
        print(f"Image captured: {filepath} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Send to Mac
        os.system(f"scp {filepath} {args.ma}:{args.rd}")
        print(f"Successfully sent {filename} to {args.ma}:{args.rd}.")

    except Exception as e:
        print(f"Error occurred: {e} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Main loop
while True:
    capture_and_send()
    print(f"Waiting for {args.i} seconds before next capture...\n")
    time.sleep(args.i)