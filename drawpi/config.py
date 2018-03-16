
# The steps per mm
STEPS_MM = 100

# Invert the direction of the motor for this axis?
X_INVERTED = False
Y_INVERTED = True

# STEP gpio pin for axis
X_STEP = 16
Y_STEP = 21

# DIR gpio pin for axis
X_DIR = 19
Y_DIR = 20

# GPIO pin for enabling steppers
ENABLE_STEPPER = 22

# The endstop pins
X_MIN = 4
Y_MIN = 17

# Servo Pin
PEN_SERVO = 18
# Up and down pulse lengths
PEN_UP_PULSE = 2000
PEN_DOWN_PULSE = 1000

# Maximum number of pulses per block of waves
MAX_PULSE_PER_WAVE = 680

# The feedrate for gotos(max reliable rate)
GOTO_RATE = 20

# The feedrate for zeroing
ZERO_RATE = 5

# Max extents - the size of the drawing area
X_EXTENT = 200
Y_EXTENT = 200
DEFAULTS = {
    "feedrate": 10 # MM/SECOND
}
