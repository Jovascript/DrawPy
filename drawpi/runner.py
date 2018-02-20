'''DRAWPI(Y)'''
import logging
import sys
from drawpi.decode import PlotterParser
from drawpi.hardware.plotter import Plotter

def execute_line(command, plotter:Plotter):
    plotter.draw_line(plotter.location, command["finish"], command["feedrate"])

def execute_goto(command, plotter:Plotter):
    plotter.goto(command["finish"])

def execute_pen(command, plotter:Plotter):
    if command["state"]:
        plotter.penup()
    else:
        plotter.pendown()

def execute_zero(command, plotter:Plotter):
    plotter.zero()

COMMANDS = {
    "goto": execute_goto,
    "line": execute_line,
    "zero": execute_zero,
    "pen": execute_pen
}

def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

def main(commands):
    parser = PlotterParser(commands)
    plotter = Plotter()
    parsed = list(parser)
    for command in parsed:
        COMMANDS[command["type"]](command, plotter)


