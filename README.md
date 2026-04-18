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

## Cloudflare Tunnel Setup

### Step 1: Install cloudflared

```bash
# Download latest ARM build for Pi Zero 2 W
cd ~
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm

# Make executable and move to system path
chmod +x cloudflared-linux-arm
sudo mv cloudflared-linux-arm /usr/local/bin/cloudflared

# Verify installation
cloudflared version
```

### Step 2: Authenticate with Cloudflare

```bash
# This opens a browser link to authenticate
cloudflared tunnel login

## You'll see output like:
# A browser window should have opened at the following URL:

# https://dash.cloudflare.com/argotunnel?callback=https%3A%2F%2Flocalhost%3A...

# If not, please visit the URL above in your browser.

# 1. Copy that URL and open it on any device (phone, laptop, etc.)
# 2. Select your Cloudflare domain or create a free one (e.g., `your-domain.workers.dev`)
# 3. Authorize — this downloads a certificate to your Pi at `~/.cloudflared/cert.pem`
```

### Step 3: Create a Permanent Tunnel

```bash
# Create the tunnel (name it whatever you want)
cloudflared tunnel create rpi-chicken-coop

# Output shows your tunnel ID, save this:
# Tunnel credentials written to /home/pi/.cloudflared/<UUID>.json
# Your tunnel ID is: <UUID>
```

### Step 4: Configure the Tunnel
Create a config file:

```bash
vim ~/.cloudflared/config.yml
```
Add this content (replace <YOUR_TUNNEL_ID> with the ID from step 3):

``` yaml
yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /home/picoop-admin/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  - hostname: coop.your-domain.workers.dev
    service: http://localhost:8000
  - service: http_status:404
```
### Step 5: Route DNS to Your Tunnel

``` bash
# Create a DNS record pointing to your tunnel
# Replace with your actual domain and tunnel ID
cloudflared tunnel route dns rpi-chicken-coop coop.your-domain.workers.dev
```

### Step 6: Test the Tunnel
```bash
# Start the tunnel manually to verify
cloudflared tunnel run rpi-chicken-coop
```
You should see:

```bash
2024-XX-XXTXX:XX:XXZ INF Connection registered       connIndex=0 ...
```
Now visit https://coop.your-domain.workers.dev — it should show your chicken coop interface!

Stop the test with Ctrl+C.

## Cloudflare Systemd Service (Auto-Start on Boot)

### Step 7: Create Service File
```bash
sudo vim /etc/systemd/system/cloudflared-chicken-coop.service
```
Add this:

```ini
[Unit]
Description=Cloudflare Tunnel for Chicken Coop
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=picoop-admin
Group=picoop-admin
WorkingDirectory=/home/picoop-admin
ExecStart=/usr/local/bin/cloudflared tunnel run rpi-chicken-coop
Restart=always
RestartSec=5

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
```

### Step 8: Enable and Start Service
```bash
# Reload systemd to pick up new service
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable cloudflared-chicken-coop.service

# Start now
sudo systemctl start cloudflared-chicken-coop.service

# Check status
sudo systemctl status cloudflared-chicken-coop.service
```
You should see active (running).

## Run the web server stuff as a service (so it will survive restarts):

``` bash
sudo vim /etc/systemd/system/chicken-coop-api.service
```

```ini
[Unit]
Description=Chicken Coop FastAPI Server
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=picoop-admin
Group=picoop-admin
WorkingDirectory=/home/picoop-admin/rpi-chicken-coop

# Activate venv and run uvicorn
ExecStart=/home/picoop-admin/rpi-chicken-coop/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=5

# Environment
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable chicken-coop-api.service
sudo systemctl start chicken-coop-api.service
sudo systemctl status chicken-coop-api.service
```