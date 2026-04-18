# servo.py
import logging
from gpiozero import AngularServo

logger = logging.getLogger(__name__)


class ServoController:
    def __init__(self, gpio_pin=18, min_angle=-90, max_angle=90):
        self.min_angle = min_angle
        self.max_angle = max_angle
        
        self.servo = AngularServo(
            gpio_pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=0.0005,
            max_pulse_width=0.0025
        )
        
        self.current_angle = 0
        self.set_angle(0)
        logger.info(f"Servo initialized on GPIO {gpio_pin}")
    
    def set_angle(self, angle: int):
        clamped = max(self.min_angle, min(self.max_angle, angle))
        self.servo.angle = clamped
        self.current_angle = clamped
        logger.info(f"Servo moved to {clamped}°")
        return clamped
    
    def close(self):
        self.servo.detach()
        logger.info("Servo detached")