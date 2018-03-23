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
        # Setup the pigpio pi representation
        self.pi = pigpio.pi()
        # Setup pins as outputs/inputs
        self.setup_pins()
        # Initialise the pulse sender thread
        self.pulse_manager = XYSteppers(self.pi)
        logger.info("Plotter is ready")

    def _get_steps_to(self, point):
        # Get the steps to a point
        diff = point - self.location
        return diff.x, diff.y

    def goto(self, point, wait=True):
        logger.info("GOTO " + str(point))
        # Get no. steps to endpoint
        x, y = self._get_steps_to(point)
        dirx = diry = 1
        # If steps are negative, change direction and make steps positive
        if (x < 0):
            dirx = 0
            x = abs(x)
        if (y < 0):
            diry = 0
            y = abs(y)
        # Rate is a frequency, get us between pulses
        delay_per_pulseset = frequency_to_delay(mm_to_steps(config.GOTO_RATE))
        pulses = []
        # Add pulses until correct no. of steps is achieved.
        while (x > 0) or (y > 0):
            # Set delay to make speed consistent.
            if x > 0 and y > 0:
                delay = delay_per_pulseset/2
            else:
                delay = delay_per_pulseset
            # If there is still stuff for an axis, move
            if x > 0:
                pulses.append([config.X_STEP, delay])
                x -= 1
            if y > 0:
                pulses.append([config.Y_STEP, delay])
                y -= 1
        
        logger.debug("GOTO generated {} pulses".format(len(pulses)))
        # If there are pulses, execute them
        if len(pulses):
            self._execute_move(dirx, diry, pulses, wait)
        # Update location
        self.location = point

    def penup(self):
        '''Set servo to move pen up'''
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)
        time.sleep(config.PEN_MOVE_DELAY)

    def pendown(self):
        '''Set servo to move pen down'''
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_DOWN_PULSE)
        time.sleep(config.PEN_MOVE_DELAY)

    def zero_me(self):
        '''Zero the plotter(move it to home)'''
        # The delay in us
        delay = frequency_to_delay(mm_to_steps(config.ZERO_RATE))
        # For each axis
        for stepp, dirp, inverted, triggerp in [
            [config.X_STEP, config.X_DIR, config.X_INVERTED, config.X_MIN],
                                      [config.Y_STEP, config.Y_DIR,
                                          config.Y_INVERTED, config.Y_MIN]
                                      ]:

            # Set movement dirextion
            self.pi.write(dirp, inverted)
            pulses = []
            # Add steps to account for the most extreme situation
            steps = mm_to_steps(config.X_EXTENT)
            for i in range(steps):
                pulses.append([stepp, delay])
            self.pi.write(config.ENABLE_STEPPER, 0)
            # Execute pulses(without waiting for completion)
            self.pulse_manager.execute_pulses(pulses)
            # Wait until endstop switch is pressed
            while not self.pi.read(triggerp):
                pass
            # Disable the steppers
            self.pi.write(config.ENABLE_STEPPER, 1)
            # Stop the thing
            self.pulse_manager.slow_stop()
            # Wait for it to stop making pulses
            self.pulse_manager.done.wait()
        # We are now zeroed.
        self.location = Point(0,0)


            

    def draw_line(self, start, finish, rate):
        logger.info("LINE from {} to {}".format(str(start), str(finish)))
        # ensure at start point
        self.goto(start)
        # calculate stepped finish
        x, y = self._get_steps_to(finish)
        # Calculate directions
        dir_x = x > 0
        dir_y = y > 0
        # generate pulses
        pulses = self._generate_line_pulses((x,y), mm_to_steps(rate))
        logger.debug("LINE generated {} pulses".format(len(pulses)))
        # execute thing
        if len(pulses):
            self._execute_move(dir_x, dir_y, pulses)
        self.location = finish

    def _generate_line_pulses(self, finish, rate):
        pulses = []

        x = y = 0
        dx, dy = finish
        # Distance, absolute
        dy = abs(dy)
        dx = abs(dx)

        fxy = dx - dy
        delay = frequency_to_delay(rate)

        while((x != dx) or (y != dy)):
            # The endpoint has not been reached
            # Works along the line in zigzag, going towards 'ideal' until achieved
            # and then switching to other axis
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
        # Stepper driver pins are outputs
        self.pi.set_mode(config.X_DIR, pigpio.OUTPUT)
        self.pi.set_mode(config.X_STEP, pigpio.OUTPUT)
        self.pi.set_mode(config.Y_DIR, pigpio.OUTPUT)
        self.pi.set_mode(config.Y_STEP, pigpio.OUTPUT)

        # Set servo to default pen up position.
        self.pi.set_mode(config.PEN_SERVO, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)

        # Disable steppers until we need to do stuff
        self.pi.set_mode(config.ENABLE_STEPPER, pigpio.OUTPUT)
        self.pi.write(config.ENABLE_STEPPER, 1)

    def _execute_move(self, dirx, diry, pulses, wait=True):
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

        # Send to the pulse thread
        self.pulse_manager.execute_pulses(pulses)

        # If we want to wait
        if wait:
            # Wait for all the pulses to have been sent
            self.pulse_manager.done.wait()
            # Disable steppers once more
            self.pi.write(config.ENABLE_STEPPER, 1)
            logger.debug("Done executing pulses")
