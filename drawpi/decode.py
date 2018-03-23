'''Decode the instructions'''
COMMANDS = ["SP", "ZE", "PU", "PD", "LN", "GT"]
import logging
import drawpi.config
logger = logging.getLogger(__name__)
from drawpi.point import Point


class ParseError(Exception):
    '''Error in parsing the provided commands'''
    pass


class PlotterParser:
    COMMANDS = ["SP", "ZE", "PU", "PD", "LN", "GT"]

    def __init__(self, commands):
        # The command text
        self.text = commands
        # Default settings
        self.settings = drawpi.config.DEFAULTS
        # The line no. (for error messages)
        self.line = 0
        # The parsers for each command'''
        self.COMMAND_PARSERS = [
            self.parse_feedrate,
            self.parse_gotozero,
            self.parse_penup,
            self.parse_pendown,
            self.parse_line,
            self.parse_goto
        ]
        self.begin_parsing()

    def parse_error(self, message):
        raise ParseError("Line {}: {}".format(self.line, message))

    def parse_feedrate(self, command):
        if not len(command) == 2:
            self.parse_error("SP must specify one feedrate.")
        else:
            try:
                self.settings["feedrate"] = int(command[1])
            except ValueError:
                self.parse_error("Invalid feedrate value.")
        return 0

    def parse_line(self, command):
        if len(command) == 3:
            # End coord
            try:
                retcom =  {
                    "type": "line",
                    "finish": Point(float(command[1]), float(command[2])),
                    "feedrate": self.settings["feedrate"]
                }
                return retcom
            except ValueError:
                self.parse_error("Invalid Coordinate Values")
        else:
            self.parse_error("LN must specify end coords.")

    def parse_goto(self, command):
        if len(command) == 3:
            # End coord
            try:
                retcom =  {
                    "type": "goto",
                    "finish": Point(float(command[1]), float(command[2]))
                }
                return retcom
            except ValueError:
                self.parse_error("Invalid Coordinate Values")
        else:
            self.parse_error("GT must specify end coords.")
    
    def parse_gotozero(self, command):
        if len(command) == 1:
            return {"type": "zero"}
        else:
            self.parse_error("Invalid ZE command.")

    def parse_pendown(self, command):
        if len(command) == 1:
            return {"type": "pen", "state": True}
        else:
            self.parse_error("Invalid PD command.")

    def parse_penup(self, command):
        if len(command) == 1:
            return {"type": "pen", "state": False}
        else:
            self.parse_error("Invalid PU command.")
        

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        try:
            command = self.commands[self.line].strip().split()
        except IndexError:
            raise StopIteration
        self.line += 1
        if len(command):
            if not command[0] in self.COMMANDS:
                raise ParseError(
                    "Not a valid command at line {}".format(self.line))
            else:
                com = self.COMMAND_PARSERS[self.COMMANDS.index(command[0])](command)
                if com:
                    return com
                else:
                    return self.next()
        else:
            return self.next()

    def begin_parsing(self):
        self.commands = self.text.split('\n')


