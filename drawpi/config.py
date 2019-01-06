
# The steps per mm
STEPS_MM = 50

# Invert the direction of the motor for this axis?
X_INVERTED = True
Y_INVERTED = False

# STEP gpio pin for axis
X_STEP = 16
Y_STEP = 21

# DIR gpio pin for axis
X_DIR = 19
Y_DIR = 20

# GPIO pin for enabling steppers
ENABLE_STEPPER = 22

# The endstop pins
X_MIN = 17
Y_MIN = 4

X_END_INVERTED = True
Y_END_INVERTED = True

# Servo Pin
PEN_SERVO = 18
# Up and down pulse lengths
PEN_UP_PULSE = 2300
PEN_DOWN_PULSE = 1540
# Time for servo to move in seconds.
PEN_MOVE_DELAY = 0.5


# The feedrate for gotos(max reliable rate)
GOTO_RATE = 25

# The feedrate for zeroing
ZERO_RATE = 8

# Max extents - the size of the drawing area
X_EXTENT = 200
Y_EXTENT = 200
DEFAULTS = {
    "feedrate": 25 # MM/SECOND
}


PREFERRED_PULSE_BATCH = 1000
