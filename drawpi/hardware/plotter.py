from drawpi import config
from drawpi.point import Point
from drawpi.utils import frequency_to_delay, mm_to_steps
from drawpi.hardware.steppers import XYSteppers
from drawpi.logutils import get_logger
import time
import pigpio

logger = get_logger("hardware.Plotter")
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
        x, y = self._get_steps_to(point)
        dirx = diry = 1
        if (x<0):
            dirx = 0
            x = abs(x)
        if (y<0):
            diry = 0
            y = abs(y)
        delay = frequency_to_delay(config.DEFAULT_FEEDRATE)
        pulses = []
        while (x>0) or (y>0):
            if x > 0:
                pulses.append([config.X_STEP, delay])
            if y > 0:
                pulses.append([config.Y_STEP, delay])
        logger.debug("GOTO generated {} pulses".format(len(pulses)))
        self._execute_move(dirx, diry, pulses)
            

    
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
        self.pi.set_mode(config.ENABLE_STEPPER, pigpio.OUTPUT)
        self.pi.write(config.ENABLE_STEPPER, 1)

    def _execute_move(self, dirx, diry, pulses):
        # Enable Steppers
        self.pi.write(config.ENABLE_STEPPER, 1)

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

        self.pulse_manager.busy.wait()
        self.pi.write(config.ENABLE_STEPPER, 1)
