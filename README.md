# Remote Chicken Coop - Proof of Concept

This repo is meant to be a repository of the code needed to use a Raspberry Pi board for running a chicken coop remotely.

Currently this is a proof of concept, A simple FastAPI-based web interface for remote camera viewing and servo control on a Raspberry Pi Zero 2 W.

TODO: Currently this is geared towards someone who is rather familiar with all of the associated technologies. It might be nice to eventually redo this to i either additionally or instead of this - make it so that this is a true walk-through for someone who is very unfamiliar with Raspberry Pi stuff.

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Pi Camera Module (with Zero camera cable)
- SG90 or similar hobby servo
- Jumper wires

## Wiring

| Servo Wire             | Pi Zero 2 W Pin  |
| ---------------------- | ---------------- |
| Red (power)            | 5V (pin 2)       |
| Brown/Black (ground)   | GND (pin 6)      |
| Orange/Yellow (signal) | GPIO 17 (pin 11) |

## Flash Raspberry Pi OS

Download Raspberry Pi Imager
Select Raspberry Pi OS Lite (64-bit).

Configure advanced settings:
    Enable SSH
    Set username/password (most of this assumes a username of `picoop-admin`)
    Configure WiFi (SSID + password + country(?))
    Set hostname (e.g., pi-cam)

Flash to microSD and boot the Pi.

## Raspberry Pi Setup Commands

`ssh picoop-admin@pi-coop.local`
(or use the Pi’s IP address)

```bash
# Update system (this may take a while)
sudo apt update && sudo apt upgrade -y

# Install system dependencies (also may take a while)
sudo apt install -y python3-pip python3-venv ffmpeg v4l-utils git motion vim python3-picamera2 libcap-dev

# install pigpio by building it from the source (also will take a few minutes)
sudo ./install_pigpio.sh

# verify has rpicam: this should return something.
which rpicam-still
```

Edit `/boot/firmware/config.txt` with `sudo vim /boot/firmware/config.txt` (see here: https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/12MP-IMX708/)
    change `camera_auto_detect=1` to `camera_auto_detect=0`
    Locate the line [all] and add the following line below it:
        `dtoverlay=imx708` (you may need it to be different depending on what camera you have. Check out the arducam docs for more info)
    
reboot with `sudo reboot` 

``` bash

# Get all of the code from github
git clone https://github.com/jstephencorey/rpi-chicken-coop.git
cd rpi-chicken-coop

# Create virtual environment
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Install Python dependencies from the requirements file
pip install -r requirements.txt

# note that there were some slightly weird things that happened with PyCamera-2, so you may need to try reinstalling it a few times and reboot it

# run it:
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure