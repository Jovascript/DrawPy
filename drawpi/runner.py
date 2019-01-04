'''DRAWPI(Y)'''
import logging
import sys
from drawpi.decode import PlotterParser
from drawpi.hardware.plotter import Plotter

def execute_line(command, plotter:Plotter):
    '''Line is slower and prettier.'''
    plotter.draw_line(plotter.location, command["finish"], command["feedrate"])

def execute_goto(command, plotter:Plotter):
    '''Goto is fast and not pretty'''
    plotter.goto(command["finish"])

def execute_pen(command, plotter:Plotter):
    '''Run a pen change command'''
    if command["state"]:
        plotter.penup()
    else:
        plotter.pendown()

def execute_zero(command, plotter:Plotter):
    '''Zero the plotter'''
    plotter.zero_me()


# Dictionary of command name to function to run.
COMMANDS = {
    "goto": execute_goto,
    "line": execute_line,
    "zero": execute_zero,
    "pen": execute_pen
}

def setup_logging(verbose=False):
    '''Setup logging for everything else'''
    level = logging.DEBUG if verbose else logging.info
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=level)

def main(commands):
    # Initialise command parser(parses jcode)
    parser = PlotterParser(commands)
    # Initialise the plotter, steppers etc.
    plotter = Plotter()
    parsed = list(parser)
    # Run commands, one by one, according to the appropriate function.
    try:
        for command in parsed:
            COMMANDS[command["type"]](command, plotter)
    finally:
        plotter.stop()



