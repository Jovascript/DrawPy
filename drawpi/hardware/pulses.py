from drawpi.point import Point


class PulseProducer:
    def __init__(self, commands):
        self.commands = commands
        self.position = Point(0,0)

    def _get_steps_to(self, end):
        diff = end - self.position
        return diff.x, diff.y

    def __iter__():
        for command in self.commands:
            if command["type"] == "line":
                pulses = line_pulses(position, command["finish"], command["feedrate"]):
            elif command["type"] == "goto":
                pulses = goto_pulses(command["finish"])
            elif command["type"] == "zero":
                pulses = zero_pulses()
            elif command["type"] == "pen":
                pulses = pen_pulses(command["state"])
            else:
                raise Exception
            for pulse in pulses:
                yield pulse

    def line_pulses(end, feedrate):
    