from drawpi import config
from drawpi.point import Point
from drawpi.utils import frequency_to_delay, mm_to_steps
from drawpi.hardware.steppers import XYSteppers
import logging
import time
import pigpio
from drawpi.hardware.hardware_internals.rpgpio import GPIO, DMAGPIO

logger = logging.getLogger(__name__)


class Plotter:
    '''Manages the plotter, and its capabilities'''

    def __init__(self):
        # Store location in STEPS
        self.location = Point(0, 0)

        # Store current direction
        self.direction = (True, True)


        self.gpio = GPIO()
        self.dma = DMAGPIO()
        self.pi = pigpio.pi()

        # Setup pins as outputs/inputs
        self.setup_pins()

        self.pulses = []

        logger.info("Plotter is ready")

    def _get_pulse(self, pins, delay=0):
        setmask = 0
        resetmask = 0
        for pin, state in pins.items():
            if state:
                setmask |= 1 << pin
            else:
                resetmask |= 1 << pin
        return (setmask, resetmask, delay)

    def add_pulse(self, pulse):
        self.pulses.append((pulse[0], pulse[1]))
        logger.debug("Added pulse {}".format((pulse[0], pulse[1])))
        if len(pulse) > 2:
            self.pulses.append((pulse[2],))
            logger.debug("Added pulse {}".format((pulse[2],))
        if len(self.pulses) > config.PREFERRED_PULSE_BATCH:
            logger.debug("Committing Pulses")
            # Enable steppers
            self.gpio.clear(config.ENABLE_STEPPER)
            self.dma.add_pulses(self.pulses)
            self.pulses = []
            self.dma.update()

    def flush_pulses(self):
        logger.debug("Flushing Pulses")
        self.dma.add_pulses(self.pulses)
        self.pulses = []
        self.dma.update()

    def wait_till_idle(self):
        self.flush_pulses()
        logger.debug("Waiting till Idle")
        while self.dma.is_active():
            self.dma.update()
            time.sleep(0.1)

    def stop(self):
        # Disable the steppers first
        self.gpio.set(config.ENABLE_STEPPER)
        self.dma.stop()

    def shutdown(self):
        '''Shutdown tidily'''
        self.stop()
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)
        self.pi.stop()


    def _set_direction(self, dirX, dirY):
        set = 0
        reset = 0
        if dirX != config.X_INVERTED:
            set |= 1 << config.X_DIR
        else:
            reset |= 1 << config.X_DIR
        if dirY != config.Y_INVERTED:
            set |= 1 << config.Y_DIR
        else:
            reset |= 1 << config.Y_DIR
        self.add_pulse((set, reset, 0))

    def _pulse_steppers(self, stepx, stepy, delay):
        bitmask = 0
        if stepx:
            bitmask |= 1 << config.X_STEP
        if stepy:
            bitmask |= 1 << config.Y_STEP
        self.add_pulse((bitmask, 0, int(delay / 2)))
        self.add_pulse((0, bitmask, int((delay + 1) / 2)))

    def _get_steps_to(self, point):
        # Get the steps to a point
        diff=point - self.location
        return diff.x, diff.y

    def goto(self, point):
        logger.info("GOTO " + str(point))
        # Get no. steps to endpoint
        x, y=self._get_steps_to(point)
        dirx=diry=True
        # If steps are negative, change direction and make steps positive
        if (x < 0):
            dirx=False
            x=abs(x)
        if (y < 0):
            diry=False
            y=abs(y)

        # Add the pulse for setting the direction
        self._set_direction(dirx, diry)
        # Rate is a frequency, get us between pulses
        delay_per_pulseset=frequency_to_delay(mm_to_steps(config.GOTO_RATE))

        # -DEBUG-
        pulse_count=0

        # Add pulses until correct no. of steps is achieved.
        while (x > 0) or (y > 0):
            # Decrement
            if x > 0:
                x -= 1
            if y > 0:
                y -= 1
            # Add the pulse for the steppers
            self._pulse_steppers(x > 0, y > 0, delay_per_pulseset)
            pulse_count += 1

        logger.debug("GOTO generated {} pulses".format(pulse_count))
        # Update location
        self.location=point

    def penup(self):
        '''Set servo to move pen up'''
        self.wait_till_idle()
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)
        time.sleep(config.PEN_MOVE_DELAY)

    def pendown(self):
        '''Set servo to move pen down'''
        self.wait_till_idle()
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_DOWN_PULSE)
        time.sleep(config.PEN_MOVE_DELAY)

    def zero_me(self):
        '''Zero the plotter(move it to home)'''
        # The delay in us
        delay=frequency_to_delay(mm_to_steps(config.ZERO_RATE))

        # 1 Second of waves are generated at a time(just in case)
        safety_pregen_no=mm_to_steps(config.ZERO_RATE)
        # For each axis
        for is_x, triggerp, extent, endinverted in [
            [True,
                config.X_MIN, config.X_EXTENT, config.X_END_INVERTED],
            [False, config.Y_MIN, config.Y_EXTENT, config.Y_END_INVERTED]
                                      ]:

            self.wait_till_idle()

            theoretical_maximum_steps = mm_to_steps(extent)
            steps_moved = 0
            while steps_moved < theoretical_maximum_steps:
                # This limits just in case of malfunction (inversion for endstops -> high when pressed)
                endstop = (self.gpio.read(triggerp) == 1) == endinverted
                if endstop:
                    self.stop()
                    logger.info("ZERO AXIS SUCCESS")
                    break
                if not self.dma.is_active():
                    self._set_direction(False, False)
                    for _ in range(safety_pregen_no):
                        steps_moved += 1
                        self._pulse_steppers(is_x, not is_x, delay)
        # We are now zeroed.
        self.location=Point(0, 0)

    def draw_line(self, start, finish, rate):
        logger.info("LINE from {} to {}".format(str(start), str(finish)))
        # ensure at start point
        if self.location != start:
            self.goto(start)
        # Get no. steps to endpoint
        x, y=self._get_steps_to(finish)
        dirx=diry=True
        # If steps are negative, change direction and make steps positive
        if (x < 0):
            dirx=False
            x=abs(x)
        if (y < 0):
            diry=False
            y=abs(y)

        # Add the pulse for setting the direction
        self._set_direction(dirx, diry)
        # generate pulses
        pulse_count=self._generate_line_pulses((x, y), mm_to_steps(rate))
        logger.debug("LINE generated {} pulses".format(pulse_count))

        self.location=finish

    def _generate_line_pulses(self, steps, rate):
        x=y=0
        dx, dy=steps

        fxy=dx - dy
        delay=frequency_to_delay(rate)

        # -DEBUG-
        pulse_count=0
        while((x != dx) or (y != dy)):
            pulse_count += 1
            # The endpoint has not been reached
            # Works along the line in zigzag, going towards 'ideal' until achieved
            # and then switching to other axis
            if fxy > 0:
                self._pulse_steppers(True, False, delay)
                x += 1
                fxy -= dy
            else:
                self._pulse_steppers(False, True, delay)
                y += 1
                fxy += dx
        return pulse_count

    def setup_pins(self):
        # Stepper driver pins are outputs
        self.gpio.init(config.X_DIR, GPIO.MODE_OUTPUT)
        self.gpio.init(config.Y_DIR, GPIO.MODE_OUTPUT)
        self.gpio.init(config.X_STEP, GPIO.MODE_OUTPUT)
        self.gpio.init(config.Y_STEP, GPIO.MODE_OUTPUT)

        # Set servo to default pen up position.
        self.gpio.init(config.PEN_SERVO, GPIO.MODE_OUTPUT)
        self.pi.set_servo_pulsewidth(config.PEN_SERVO, config.PEN_UP_PULSE)

        # Disable steppers for now
        self.gpio.init(config.ENABLE_STEPPER, GPIO.MODE_OUTPUT)
        self.gpio.set(config.ENABLE_STEPPER)

