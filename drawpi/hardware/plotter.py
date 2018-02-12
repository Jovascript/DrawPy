class Plotter:
    '''Manages the plotter, and its capabilities'''

    STEPX = 21
    STEPY = 16
    
    def __init__(self):
        pass


    def draw_line(self, start, finish, rate):
        # ensure at start point
        # calculate relative distance
        # Calculate directions
        dir_x = x < 0
        dir_y = y < 0
        # generate pulses
        # execute thing
        pass

    def _generate_line_pulses(self, finish, rate):
        pulses = []

        x = y = 0
        dx, dy = finish

        dy = abs(dy)

        dx = abs(dx)

        fxy = dx - dy
        delay = ((10**6)/rate)/2

        while((x != dx) or (y != dy)):
            # The endpoint has not been reached
            if fxy > 0:
                pulses.append([self.STEPX, 1, delay])
                pulses.append([self.STEPX, 0, delay])
                x += 1
                fxy -= dy
            else:
                pulses.append([self.STEPY, 1, delay])
                pulses.append([self.STEPY, 0, delay])
                y += 1
                fxy += dx


