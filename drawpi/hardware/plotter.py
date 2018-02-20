from drawpi import config
from drawpi.point import Point
from drawpi.utils import frequency_to_delay, mm_to_steps
from drawpi.hardware.steppers import XYSteppers
import logging
import time
import pigpio

logger = logging.getLogger(__name__)
class Plotter:
    '''Manages the plotter, and its capabilities'''

    def __init__(self):
        # Store location in STEPS
        self.location = Point(0, 0)
        self.pi = pigpio.pi()
        self.setup_pins()
        self.pulse_manager = XYSteppers(self.pi)
        logger.info("Plotter is ready")


    def _get_steps_to(self, point):
        diff = point - self.location
        return diff.x, diff.y

    def goto(self, point):
        logger.info("GOTO "+str(point))
        # Get no. steps to endpoint
        x, y = self._get_steps_to(point)
        dirx = diry = 1
        # If steps are negative, change direction and make steps positive
        if (x<0):
            dirx = 0
            x = abs(x)
        if (y<0):
            diry = 0
            y = abs(y)
        # Rate is a frequency, get us between pulses
        delay = frequency_to_delay(mm_to_steps(config.GOTO_RATE))
        pulses = []
        # Add pulses until correct no. of steps is achieved.
        while (x>0) or (y>0):
            if x > 0:
                pulses.append([config.X_STEP, delay])
                x -= 1
            if y > 0:
                pulses.append([config.Y_STEP, delay])
                y -= 1
        logger.debug("GOTO generated {} pulses".format(len(pulses)))
        self._execute_move(dirx, diry, pulses)
        # Update location
        self.location = point

    def penup(self):
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)

    def pendown(self):
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_DOWN_PULSE)
    
    def draw_line(self, start, finish, rate):
        logger.info("LINE from {} to {}".format(str(start), str(finish)))
        # ensure at start point
        self.goto(start)
        # calculate stepped finish
        x, y = self._get_steps_to(finish)
        # Calculate directions
        dir_x = x < 0
        dir_y = y < 0
        # generate pulses
        pulses = self._generate_line_pulses(finish, mm_to_steps(rate))
        logger.debug("LINE generated {} pulses".format(len(pulses)))
        # execute thing
        self._execute_move(dir_x, dir_y, pulses)
        self.location = finish

    def _generate_line_pulses(self, finish, rate):
        pulses = []

        x = y = 0
        dx, dy = finish

        dy = abs(dy)

        dx = abs(dx)

        fxy = dx - dy
        delay = frequency_to_delay(rate)

        while((x != dx) or (y != dy)):
            # The endpoint has not been reached
            if fxy > 0:
                pulses.append([config.X_STEP, delay])
                x += 1
                fxy -= dy
            else:
                pulses.append([config.Y_STEP, delay])
                y += 1
                fxy += dx
        return pulses

    def setup_pins(self):
        self.pi.set_mode(config.X_DIR, pigpio.OUTPUT)
        self.pi.set_mode(config.X_STEP, pigpio.OUTPUT)
        self.pi.set_mode(config.Y_DIR, pigpio.OUTPUT)
        self.pi.set_mode(config.Y_STEP, pigpio.OUTPUT)

        self.pi.set_mode(config.PEN_SERVO, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)

        self.pi.set_mode(config.ENABLE_STEPPER, pigpio.OUTPUT)
        self.pi.write(config.ENABLE_STEPPER, 1)

    def _execute_move(self, dirx, diry, pulses):
        logger.debug("Executing pulses")
        # Enable Steppers
        self.pi.write(config.ENABLE_STEPPER, 0)

        # If you've wired the stepper wrong(hehe)
        if config.X_INVERTED:
            dirx = not dirx
        if config.Y_INVERTED:
            diry = not diry


        # Set direction
        # TODO: Rewrite to support changing directions..
        self.pi.write(config.X_DIR, dirx)
        self.pi.write(config.Y_DIR, diry)

        self.pulse_manager.execute_pulses(pulses)

        self.pulse_manager.done.wait()
        self.pi.write(config.ENABLE_STEPPER, 1)
        logger.debug("Done executing pulses")
