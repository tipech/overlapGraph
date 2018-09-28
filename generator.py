"""Randomly generate overlapping objects in space.

Provides generator classes for the different shapes of the overlap problem, as
 well as a generator superclass for common functions such as printing or I/O.
Moreover, this can be executed as a script to actually generate the data.

Classes:
  Generator -- handles common generator actions, such as initialization
  RectangleGenerator -- handles generation of rectangle objects
  IntervalGenerator -- handles generation of interval objects

"""
import sys, random, argparse
from shapes import IntervalObject, RectangleObject
from setuptools import setup
from graphics import *
from pprint import pprint



def main():
    """Run the generator with command-line parameters."""

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Randomly generate overlapping objects in space.")

    # positional arguments: object type, number of objects
    parser.add_argument("type", choices=["interval", "rectangle"],
        help="type of overlapping objects")
    parser.add_argument("number", metavar="N", type=int,
        help="number of generated objects")

    # optional arguments: print results, draw results with graphics
    parser.add_argument("-p", "--print", action="store_true",
        help="print results to console")
    parser.add_argument("-g", "--graphics", action="store_true",
        help="display graphics and draw results")
    
    # extra optional arguments: area size, min & max object size ratios
    parser.add_argument("--area", type=int, default=1000,
        help="size of generated area (default: 1000)")
    parser.add_argument("--min", type=float, default=0.01,
        help="min ratio of object size relative to area (def: 0.01)")
    parser.add_argument("--max", type=float, default=0.1,
        help="max ratio of object size relative to area (def: 0.1)")

    # check for invalid numbers
    args = parser.parse_args()
    if args.number < 0 or args.area < 0 or args.min < 0 or args.max < 0 :
        parser.error("Invalid number argument.")
    if args.max > 1 or args.min > args.max :
        parser.error("Invalid ratios.")

    # run generator
    if args.type == "interval":
        generator = IntervalGenerator(args.number, args.area, args.min,
           args.max, 1200)
    elif args.type == "rectangle":
        generator = RectangleGenerator(args.number, args.area, args.min,
           args.max, 1200)
    
    if args.print:  # print results
        print(generator)

    if args.graphics:
        generator.draw()



class Generator():

    """Randomly generate overlapping objects in a defined space.

    Superclass that handles the common methods required for the generation,
    regardless of object type (shape).
    
    Properties:
        objects_dict -- a dictionary with all generated objects, in the form
            {"id": Object, ...}
        objects_count -- running count of generated objects 

    """

    def __init__(self, object_number, area, min_ratio, max_ratio, window):
        """Prepare space and initialize generation"""
        self.object_number = object_number
        self.area = area
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.window = window

        self.objects_dict = {}
        self.objects_count = 0

        random.seed()       # seed random number generator


    def _get_line_segment(self):
        """Get a random 1D line segment within the space boundaries"""
        point = random.randint(0, self.area) # pick random 1D point
        length = random.randint(self.area * self.min_ratio,
            self.area * self.max_ratio) # pick random length

        if point < self.area / 2: # if we"re not too close to the edge
            start = point
            end = point + length # calculate end of the interval
        else: # too close to the edge, in danger of overshooting
            end = point          # previous random point will be the end
            start = end - length # calculate start of the interval

        return (start, end)


    def _init_graphics(self):
        """Initialize the graphics environment"""
        self.win = GraphWin("Overlap", self.window + 2, self.window + 2)


    def _pause_graphics(self):
        """Pause graphics window before exit."""
        if self.win:
            self.win.getMouse() # Pause to view result
            self.win.close()


    def __repr__(self):
        """Convert to string."""
        s = ",\n".join(" %d: %r" % (id_, object_) # stringify dictionary
            for id_, object_ in self.objects_dict.items())        
        return("Generator(objects={%s}\n,count=%d)" % (s, self.objects_count))



class IntervalGenerator(Generator):

    """Randomly generate overlapping intervals in a defined space

    Methods:
        __init__ -- prepares the space and generates the intervals
        _generate_interval -- generates a single interval"""

    def __init__(self, object_number, area, min_ratio, max_ratio, window):
        """Prepare space and initialize generation"""
        super().__init__(object_number, area, min_ratio, max_ratio, window)

        self.win = None   # controller for graphics window

        # generate intervals and add them to the dictionary
        for i in range(0, self.object_number):
            new_object = self._generate_interval()
            self.objects_dict[new_object.id_] = new_object


    def _generate_interval(self):
        """Generate a single random interval within the space"""
        start, end = self._get_line_segment() # generate x axis

        # assign id based on count
        id_ = self.objects_count  
        self.objects_count += 1

        # generate interval object
        interval = IntervalObject(start, end, id_)
        return interval


    def draw(self):
        """Draw the generated intervals"""
        self._init_graphics()

        scale = self.window / self.area           # scaling to window
        margin = self.window / self.objects_count # margin between each result

        # draw each rectangle
        for interval in self.objects_dict.values():
            y_coord = interval.id_ * margin + 2 # display interval based on id

            # calculate ends and center coordinates and adjust for window
            start = Point(interval.start * scale, y_coord)
            end = Point(interval.end * scale, y_coord)
            center = Point(interval.get_center() * scale, y_coord - 10)

            # create rectangle and label graphics objects
            shape = Line(start, end)
            shape.setWidth(3)
            label = Text(center, interval.id_)

            # draw rectangle and label graphics objects
            shape.draw(self.win)
            label.draw(self.win)

        self._pause_graphics()



class RectangleGenerator(Generator):

    """Randomly generate overlapping rectangles in a defined space

    Methods:
        __init__ -- prepares the space and generates the rectangles
        _generate_rectangle -- generates a single rectangle

    """

    def __init__(self, object_number, area, min_ratio, max_ratio, window):
        """Prepare space and generate rectangles"""
        super().__init__(object_number, area, min_ratio, max_ratio, window)

        self.win = None   # controller for graphics window

        # generate rectangles and add them to the dictionary
        for i in range(0, self.object_number):
            new_object = self._generate_rectangle()
            self.objects_dict[new_object.id_] = new_object  


    def _generate_rectangle(self):
        """Generate a single random rectangle within the space"""
        x_start, x_end = self._get_line_segment() # generate x axis
        y_start, y_end = self._get_line_segment() # generate y axis
        
        # assign id based on count
        id_ = self.objects_count  
        self.objects_count += 1

        # generate rectangle object
        rectangle = RectangleObject(x_start, y_start, x_end, y_end, id_)
        return rectangle


    def draw(self):
        """Draw the generated rectangles"""
        self._init_graphics() # init window

        scale = self.window / self.area # scaling to window

        # draw each rectangle
        for rectangle in self.objects_dict.values():
            
            # retrieve corners and center coordinates and adjust for window
            corner_1 = Point(rectangle.x1 * scale, rectangle.y1 * scale + 2)
            corner_2 = Point(rectangle.x2 * scale, rectangle.y2 * scale + 2)
            x_center, y_center = rectangle.get_center()
            center = Point(x_center * scale, y_center * scale + 2)

            # create rectangle and label graphics objects
            shape = Rectangle(corner_1, corner_2)
            label = Text(center, rectangle.id_)

            # draw rectangle and label graphics objects
            shape.draw(self.win)
            label.draw(self.win)

        self._pause_graphics() # pause window with results until click


        

if __name__ == "__main__":
    # Run the generator with command-line parameters.
    main()