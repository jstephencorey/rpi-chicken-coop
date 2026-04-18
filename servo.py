# servo.py
import logging
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

logger = logging.getLogger(__name__)


class ServoController:
    def __init__(self, gpio_pin=17, min_angle=-90, max_angle=90):
        self.gpio_pin = gpio_pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        
        # Use pigpio for better servo timing accuracy
        try:
            factory = PiGPIOFactory()
            self.servo = AngularServo(
                gpio_pin,
                min_angle=min_angle,
                max_angle=max_angle,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
                pin_factory=factory
            )
            logger.info(f"Servo initialized on GPIO {gpio_pin}")
        except Exception:
            # Fallback to default pin factory if pigpio not available
            logger.warning("pigpio not available, using default pin factory")
            self.servo = AngularServo(
                gpio_pin,
                min_angle=min_angle,
                max_angle=max_angle
            )
        
        self.current_angle = 0
        self.set_angle(0)
    
    def set_angle(self, angle: int):
        """Set servo angle, clamped to valid range."""
        clamped = max(self.min_angle, min(self.max_angle, angle))
        self.servo.angle = clamped
        self.current_angle = clamped
        logger.info(f"Servo moved to {clamped}°")
        return clamped
    
    def close(self):
        # Detach servo to stop jitter when not in use
        self.servo.detach()
        logger.info("Servo detached")