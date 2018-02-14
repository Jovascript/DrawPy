'''Class Point, for easy representaion and manipulation'''
import drawpi.utils as utils

class Point(complex):
    def __init__(self, x, y, unit='mm'):
        if unit == 'mm':
            x = utils.mm_to_steps(x)
            y = utils.mm_to_steps(y)
        super().__init__(x, y)

    @property
    def x(self):
        return self.real

    @x.setter
    def x(self, value):
        self.real = value

    @property
    def y(self):
        return self.imag

    @y.setter
    def y(self, value):
        self.imag = value
    
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

