# Install required dependencies
cd ~
sudo apt install -y python3-setuptools python3-full wget build-essential

# Download the latest pigpio release (v79 as of now)
wget https://github.com/joan2937/pigpio/archive/refs/tags/v79.tar.gz

# Extract and build
tar zxf v79.tar.gz
cd pigpio-79
make
sudo make install

# Create the pigpiod service file
sudo tee /etc/systemd/system/pigpiod.service << 'EOF'
[Unit]
Description=Pi GPIO daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/pigpiod
ExecStop=/bin/kill -TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
sudo ldconfig
sudo systemctl daemon-reload
sudo systemctl enable --now pigpiod