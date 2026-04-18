# camera.py
import io
import logging
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self, resolution=(640, 480)):
        self.resolution = resolution
        self.picam2 = None
        self._setup()
    
    def _setup(self):
        try:
            self.picam2 = Picamera2()
            
            # Configure for video streaming
            config = self.picam2.create_video_configuration(
                main={"size": self.resolution},
                controls={"FrameRate": 30}
            )
            self.picam2.configure(config)
            self.picam2.start()
            
            logger.info(f"Camera started at {self.resolution}")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def generate_frames(self):
        """Generate MJPEG stream frames."""
        while True:
            try:
                # Capture frame as JPEG
                frame = io.BytesIO()
                self.picam2.capture_file(frame, format="jpeg")
                frame.seek(0)
                data = frame.read()
                
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n'
                )
                
            except Exception as e:
                logger.error(f"Frame capture error: {e}")
                continue
    
    def close(self):
        if self.picam2:
            self.picam2.stop()
            self.picam2.close()
            logger.info("Camera stopped")