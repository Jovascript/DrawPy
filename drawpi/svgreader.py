import xml.etree.ElementTree as ET
from svg.path import parse_path, Path, Line, CubicBezier, QuadraticBezier, Arc
from svg.path.path import Move
import re

OPTIONS_DEFAULT = {
    "detail": 0.1,
    "zero_before": True,
    "zero_after": False
}

VERBOSE = False

class SVGParseException(Exception):
    pass

class Shape:
    def __init__(self, path:str, filled=False):
        if VERBOSE:
            print("Generating Path:", path)
        self.path = parse_path(path)
        self.filled = filled
    
    def get_raw(self):
        return self.path.d()

    def slice(self, options):
        '''Turns path into series of straight line moves and Pen ups and downs'''
        instructions = ""
        # We assume pen starts in up state
        pen_state = False
        for s in self.path:
            if isinstance(s, Move):
                # The move needs pen up
                if pen_state:
                    instructions += "PU\n"
                    pen_state = False
                instructions += "GT {} {}\n".format(s.start.real, s.start.imag)
            else:
                # Other units need pen down
                if not pen_state:
                    instructions += "PD\n"
                    pen_state = True
                if isinstance(s, Line):
                    instructions += "LN {} {}\n".format(s.end.real, s.end.imag)
                else:
                    length = s.length(error=1e-5)
                    if length <= options["detail"]:
                        point = s.point(1)
                        instructions += "LN {} {}\n".format(point.real, point.imag)
                    else:
                        step = options["detail"]/length
                        steps = int(1/step)
                        for x in range(steps):
                            point = s.point(x*step)
                            instructions += "LN {} {}\n".format(point.real, point.imag)
        # Leave pen up(good manners)
        if pen_state:
            instructions += "PU\n"
        return instructions


    def __str__(self):
        return "<Shape {}>".format(self.path.d())

class Group(Shape):
    def __init__(self, children:list):
        self.children = list(filter(lambda x: x is not None, children))
        self.filled = False
    
    def merge(self):
        uber_path = ""
        for sh in self.children:
            if isinstance(sh, Group):
                uber_path += sh.merge()
            else:
                uber_path += sh.get_raw()
        return uber_path

    def slice(self, options):
        instructions = ""
        for shape in self.children:
            instructions += shape.slice(options)
        return instructions
    
    def __str__(self):
        return "<Group {}>".format(', '.join([str(x) for x in self.children]))

class SVGRoot(Group):
    def slice(self, options):
        instructions = "PU\n"
        if options["zero_before"]:
            instructions += "ZE\n"
        instructions += super().slice(options)
        if options["zero_after"]:
            instructions += "ZE\n"
        return instructions



def getEllipsePath(cx, cy, rx, ry):
    return f"M {cx-rx} {cy} a {rx} {ry} 0 1 0 {rx * 2} 0 a {rx} {ry} 0 1 0 {-(rx * 2)} 0"

def getLinePath(x1, y1, x2, y2):
    return f"M {x1} {y2} L {x2} {y2}"

def getLinesPath(start_coords, *rest, closed=False):
    x, y = start_coords
    s = f"M {x} {y} "
    for (x, y) in rest:
        s += f"L {x} {y} "
    if closed:
        s += "Z"
    return s


def parse(doc):
    '''Convert to a list of path objects'''
    doc = re.sub(' xmlns="[^"]+"', '', doc, count=1)
    root = ET.fromstring(doc)
    if not root.tag == "svg":
        print(root.tag)
        raise SVGParseException("Missing <svg> tag")
    paths = []
    for c in root:
        paths.append(getPath(c))
    return SVGRoot(paths)


def getPath(elem):
    if elem.tag == "circle":
        x = float(elem.attrib["cx"])
        y = float(elem.attrib["cy"])
        r = float(elem.attrib["r"])
        return Shape(getEllipsePath(x, y, r, r))
    elif elem.tag == "ellipse":
        x = float(elem.attrib["cx"])
        y = float(elem.attrib["cy"])
        rx = float(elem.attrib["rx"])
        ry = float(elem.attrib["ry"])
        return Shape(getEllipsePath(x, y, rx, ry))
    elif elem.tag == "line":
        x = float(elem.attrib["x1"])
        y = float(elem.attrib["y1"])
        ex = float(elem.attrib["x2"])
        ey = float(elem.attrib["y2"])
        return Shape(getLinePath(x, y, ex, ey))
    elif elem.tag == "polygon" or elem.tag == "polyline":
        closed = elem.tag == "polygon"
        coordlist = elem.attrib["points"]
        # Parse list of coords
        coordlist = coordlist.replace('e-', 'NEGEXP').replace('E-', 'NEGEXP')
        # Commas and minus-signs are separators, just like spaces.
        coordlist = coordlist.replace(',', ' ').replace('-', ' -')
        coordlist = coordlist.replace('NEGEXP', 'e-')
        coordlist = [float(x) for x in coordlist.split()]
        return Shape(getLinesPath(coordlist[0], *coordlist[1:], closed=closed))
    elif elem.tag == "rect":
        x = float(elem.attrib["x"])
        y = float(elem.attrib["y"])
        ex = x + float(elem.attrib["width"])
        ey = y + float(elem.attrib["height"])
        return Shape(getLinesPath((x, y), (ex, y), (ex, ey), (x, ey), closed=True))
    elif elem.tag == "path":
        return Shape(elem.attrib["d"])
    elif elem.tag == "g":
        # Return list of elements
        return Group([getPath(x) for x in elem])
    else:
        if VERBOSE:
            print("Dont understand {}".format(elem.tag))
        return None

def slice(parsed_doc, spec_options = {}):
    options = OPTIONS_DEFAULT.copy()
    options.update(spec_options)
    return parsed_doc.slice(options)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get JCode(drawing format) for an svg file.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("input", help="the input file")
    parser.add_argument("-o", "--output", help="Output File")
    args = parser.parse_args()
    VERBOSE = args.verbose
    with open(args.input, 'r') as f:
        text = f.read()
    
    result = slice(parse(text))
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
    else:
        print(result)
