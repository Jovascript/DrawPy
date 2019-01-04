'''Class Point, for easy representaion and manipulation'''
import drawpi.utils as utils

class Point:
    def __init__(self, x, y, unit='mm'):
        # Initialise as either mm or steps
        # Internally stored as steps
        if unit == 'mm':
            self.x = utils.mm_to_steps(x)
            self.y = utils.mm_to_steps(y)
        else:
            self.x = x
            self.y = y

    
    @property
    def x_mm(self):
        '''Calculate x in millimetres'''
        return utils.steps_to_mm(self.x)

    @x_mm.setter
    def x_mm(self, value):
        self.x = utils.mm_to_steps(value)

    @property
    def y_mm(self):
        '''Calculate y in millimetres'''
        return utils.steps_to_mm(self.y)

    @y_mm.setter
    def y_mm(self, value):
        self.y = utils.mm_to_steps(value)

    def __add__(self, other):
        '''Add 2 points, returning the new point'''
        return Point(self.x + other.x, self.y + other.y, unit="steps")

    def __sub__(self, other):
        '''Subtract 2 points, returning the new point'''
        return Point(self.x - other.x, self.y - other.y, unit="steps")
    def __str__(self):
        '''Convert point to str representation'''
        return "Point({}, {})".format(self.x, self.y)
    def __repr__(self):
        '''Convert point to str representation'''
        return "Point({}, {})".format(self.x, self.y)
    def __format__(self, spec):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, Point):
            if self.x == other.x and self.y == other.y:
                return True
        return False
