from drawpi.hardware.plotter import Plotter
from drawpi.point import Point
import logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

x = Plotter()
x.goto(Point(8*200*3, 8*200*5, unit="steps"))
print("NOOT")

