from drawpi.hardware.plotter import Plotter
from drawpi.point import Point
try:
    x = Plotter()
    x.goto(Point(1,1))
except:
    raise
finally:
    x.pulse_manager.cancel()
