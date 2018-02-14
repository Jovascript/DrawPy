'''Class Point, for easy representaion and manipulation'''
import drawpi.utils as utils

class Point:
    def __init__(self, x, y, unit='mm'):
        if unit == 'mm':
            self.x = utils.mm_to_steps(x)
            self.y = utils.mm_to_steps(y)
        else:
            self.x = x
            self.y = y

    
    @property
    def x_mm(self):
        return utils.steps_to_mm(self.x)

    @x_mm.setter
    def x_mm(self, value):
        self.x = utils.mm_to_steps(value)

    @property
    def y_mm(self):
        return utils.steps_to_mm(self.y)

    @y_mm.setter
    def y_mm(self, value):
        self.y = utils.mm_to_steps(value)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, unit="steps")

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, unit="steps")
    def __str__(self):
        return ("<Point({}, {})({}mm, {}mm)>".format(self.x, self.y, self.x_mm, self.y_mm))
    def __repr__(self):
        return self.__str__()
