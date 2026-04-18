import time
from picamera2 import Picamera2
# Initialize Picamera2
picam = Picamera2()
# Configure and start the camera
config = picam.create_preview_configuration()
picam.configure(config)
picam.start()
# Wait for the camera to adjust and capture an image
time.sleep(2)
picam.capture_file("image.jpg")
# Stop and close the camera
picam.close()