# Pi Zero 2W Camera Solution
Simple camera using the Raspberry Pi Zero 2W, as well as a Camera Module 2. Takes pictures at a set interval, and uploads them to a laptop or server via SCP (Secure Copy Protocol). This is a simple solution, but it is adaptable to lots of things.

This README.md serves as a guide for setup.

## Required Components (For camera module only):
- Raspberry Pi Zero 2W
- Raspberry Pi Camera Module 2
- Micro SD Card
- Micro USB Power
- Laptop (Guide written for MacBook)

## Initial Setup
First of all, we will need to setup and configure our Pi. This will be done without the use of a GUI, via SSH-ing into it. To do this, we will need to do a bit of setup on the SD card before even booting up the Pi.

### Step 1: Flash the OS
First of all we will flash the OS to the SD card. Simple right? WRONG! We will need to flash a version of "Raspberry Pi OS Lite" to the SD card mentioned earlier. This is because installing the OS with a GUI would be wasting our precious computing resources. As well as this, we will need to enable SSH and configure a wifi network!

Select the Raspberry Pi Zero 2W from the devices menu, then select Raspberry Pi OS Lite from the OS selection menu. 

After doing this, we will need to enable SSH and configure a network for the Pi to use. Remount the SD card (it is automatically ejected from the system after flashing). First we will configure the wifi network:
-  Create a file named  `wpa_supplicant.conf`  in the boot partition with:
    
        country=GB
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        
        network={
	         ssid="YOUR_WIFI_NAME" 
	         psk="YOUR_WIFI_PASSWORD" 
	         key_mgmt=WPA-PSK
	    }

Then we will enable SSH:
-  Create an empty file named  `ssh`  (no extension) in the boot partition
-   On Mac terminal:  `touch /Volumes/boot/ssh`

### Step 2: First Boot
Now we will insert the SD card into the Pi and boot it up. Connect the usb power cable and wait around 90 seconds for it to connect to the wifi.

### Step 3: Find your Pi on the Network 
There are several ways to find your Pi:

1.  **Using mDNS**  (simplest):
    -   From your Mac terminal:  `ping raspberrypi.local`
    -   If this works, you'll see the Pi responding with its IP address
2.  **Scan your network**  (if mDNS isn't working):
    -   Install nmap:  `brew install nmap`
    -   Scan your network:  `nmap -sn 192.168.1.0/24`  (adjust the IP range to match your network)
    -   Look for devices with "Raspberry Pi" in the description
3.  **Check your router's**  connected devices list

### Step 4: SSH into the Pi
Now we are (hopefully) ready to ssh into the Pi. 

Run This command in the Mac terminal!
`ssh pi@raspberrypi.local`
Or use the IP address if you found it:
`ssh pi@192.168.1.xxx`

### Step 5: Script preparation 
#### Install the required libraries:

`pip install picamera2`

#### Make sure you can use SCP to send files to your Mac by testing the connection:

`scp test_file.txt user@mac_ip:/path/to/remote/directory`
### Step 6: Write the script
Copy the main.py into your pi using nano. 

### Step 7: Run the script!
This should now work! - See Usage

## Usage
You can run the script from the command line with various optional arguments.

### Command-line Arguments:

`-i` (default: 10): Time (in seconds) between consecutive image captures.

`-sd` (default: /path/to/camera_images): Local directory to save captured images.

`-ma` (default: user@ip): Remote Mac address (username and IP address) for SCP transfer.

`-rd` (default: ~/received_images/): Remote directory on Mac to receive the images.

#### Example:

`python capture_and_send.py -i 5 -sd "/home/pi/images" -ma "user@192.168.1.100" -rd "~/received_images/"`

This will capture images every 5 seconds, save them in /home/pi/images, and send them to the remote Mac's ~/received_images/ directory.