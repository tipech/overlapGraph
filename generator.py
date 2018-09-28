"""Randomly generate overlapping objects in space.

Provides generator classes for the different shapes of the overlap problem, as
 well as a generator superclass for common functions such as printing or I/O.
Moreover, this can be executed as a script to actually generate the data.

Classes:
  Generator -- handles common generator actions, such as initialization
  RectangleGenerator -- handles generation of rectangle objects
  IntervalGenerator -- handles generation of interval objects

"""
import sys, random
from shapes import IntervalObject, RectangleObject
from setuptools import setup
from graphics import *
from pprint import pprint



def main():
    """Run the generator with command-line parameters."""

    try:
        if "-h" in sys.argv or "--help" in sys.argv: # help argument
            raise ValueError("")

        if "-g" in sys.argv: # graphics argument
            sys.argv.remove("-g")
            graphics = True
        elif "--graphics" in sys.argv: 
            sys.argv.remove("--graphics")
            graphics = True

        if len(sys.argv) < 3 or len(sys.argv) > 6: # too few/many arguments
            raise ValueError("Incorrect usage!\n")

        object_number = int(sys.argv[2])    # number of generated objects

        # size of generated area
        area_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
        # min object size/area ratio
        min_ratio = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
        # max object size/area ratio
        max_ratio = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1

        # Type of overlap problem
        if sys.argv[1] == "rectangle":
            generator = RectangleGenerator(object_number, area_size,
                min_ratio, max_ratio)
        elif sys.argv[1] == "interval":
            generator = IntervalGenerator(object_number, area_size,
                min_ratio, max_ratio)
        else: # unknown type
            raise ValueError("Incorrect object type!\n")

        print(generator)

        if graphics:
            generator.draw()


    except ValueError as err:
        if err != "":
            print(err)
        print("Randomly generate overlapping objects in space.\n\n"
            + "Usage:\n\tgenerator.py rectangle|interval <nr_of_objects> "
            + "[--area=<size>] [--min=<ratio>] [--max=<ratio>] "
            + "[-g] | --graphics\n\tgenerator.py -h | --help\n"
            + "Options:\n\t-h --help\tShow usage\n\t"
            + "-g --graphics\tDraw the generated objects\n\t"
            + "<nr_of_objects>\tNumber of generated objects\n\t"
            + "--area=<size>\tMax size of the generated area [def: 1000]\n\t"
            + "--min=<ratio>\tMin ratio of object size/area [def: 0.01]\n\t"
            + "--max=<ratio>\tMax ratio of object size/area [def: 0.1]\n\t")


class Generator():

    """Randomly generate overlapping objects in a defined space.

    Superclass that handles the common methods required for the generation,
    regardless of object type (shape).
    
    Properties:
        objects_dict -- a dictionary with all generated objects, in the form
            {"id": Object, ...}
        objects_count -- running count of generated objects 

    """

    def __init__(self, object_number, area_size, min_ratio, max_ratio):
        """Prepare space and initialize generation"""
        self.object_number = object_number
        self.area_size = area_size
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

        self.objects_dict = {}
        self.objects_count = 0

        random.seed()       # seed random number generator


    def _get_line_segment(self):
        """Get a random 1D line segment within the space boundaries"""
        point = random.randint(0, self.area_size) # pick random 1D point
        length = random.randint(self.area_size * self.min_ratio,
            self.area_size * self.max_ratio) # pick random length

        if point < self.area_size / 2: # if we're not too close to the edge
            start = point
            end = point + length # calculate end of the interval
        else: # too close to the edge, in danger of overshooting
            end = point          # previous random point will be the end
            start = end - length # calculate start of the interval

        return (start, end)


    def _init_graphics(self):
        """Initialize the graphics environment"""
        self.win = GraphWin('Overlap', 1201, 1201)


    def _pause_graphics(self):
        """Pause graphics window before exit."""
        if self.win:
            self.win.getMouse() # Pause to view result
            self.win.close()


    def __repr__(self):
        """Convert to string."""
        s = ',\n'.join(" %d: %r" % (id_, object_) # stringify dictionary
            for id_, object_ in self.objects_dict.items())        
        return("Generator(objects={%s}\n,count=%d)" % (s, self.objects_count))



class IntervalGenerator(Generator):

    """Randomly generate overlapping intervals in a defined space

    Methods:
        __init__ -- prepares the space and generates the intervals
        _generate_interval -- generates a single interval"""

    def __init__(self, object_number, area_size, min_ratio, max_ratio):
        """Prepare space and initialize generation"""
        super().__init__(object_number, area_size, min_ratio, max_ratio)

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
        self._pause_graphics()



class RectangleGenerator(Generator):

    """Randomly generate overlapping rectangles in a defined space

    Methods:
        __init__ -- prepares the space and generates the rectangles
        _generate_rectangle -- generates a single rectangle

    """

    def __init__(self, object_number, area_size, min_ratio, max_ratio):
        """Prepare space and generate rectangles"""
        super().__init__(object_number, area_size, min_ratio, max_ratio)

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

        scale = 1200 / self.area_size
        # scale = 1

        # draw each rectangle
        for rectangle in self.objects_dict.values():
            
            # retrieve corners and center coordinates and adjust for window
            corner_1 = Point(rectangle.x1 * scale, rectangle.y1 * scale)
            corner_2 = Point(rectangle.x2 * scale, rectangle.y2 * scale)
            x_center, y_center = rectangle.get_center()
            center = Point(x_center * scale, y_center * scale)

            # create rectangle and label graphics objects
            shape = Rectangle(corner_1, corner_2)
            label = Text(center, rectangle.id_)

            # draw rectangle and label graphics objects
            shape.draw(self.win)
            label.draw(self.win)

        self._pause_graphics() # pause window with results until click


        

if __name__ == '__main__':
    # Run the generator with command-line parameters.
    main()