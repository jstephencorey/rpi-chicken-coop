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

# Update library cache and systemd
sudo ldconfig
sudo systemctl daemon-reload

# Enable and start the pigpiod service
sudo systemctl enable --now pigpiod

sudo systemctl enable pigpiod
sudo systemctl start pigpiod