"""Randomly generate overlapping objects in space.

Provides generator classes for the different shapes of the overlap problem, as
 well as a generator superclass for common functions such as printing or I/O.
Moreover, this can be executed as a script to actually generate the data.

Classes:
  Generator -- handles common generator actions, such as initialization
  RectangleGenerator -- handles generation of rectangle objects
  IntervalGenerator -- handles generation of interval objects

"""
import sys, random, argparse, json, os
from shapes import IntervalObject, RectangleObject
from graphics import Point, Line, Rectangle, Text, GraphWin
from datetime import datetime
from pprint import pprint



def main():
    """Run the generator with command-line parameters."""

    window_size = 1200

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Randomly generate overlapping objects in space.")

    # positional arguments: object type
    parser.add_argument("type", choices=["interval", "rectangle"],
        help="type of overlapping objects")

    # optional arguments: print results, draw results with graphics
    parser.add_argument("-p", "--print", action="store_true",
        help="print results to console")
    parser.add_argument("-g", "--graphics", action="store_true",
        help="display graphics and draw results")
    parser.add_argument("-s", "--store", action="store_true",
        help="store data to file")
    
    # extra optional arguments: number of objects, area, min & max size ratios
    parser.add_argument("--number", metavar="N", type=int, default=20,
        help="number of generated objects")
    parser.add_argument("--area", type=int, default=1000,
        help="size of generated area (default: 1000)")
    parser.add_argument("--min", type=float, default=0.01,
        help="min ratio of object size relative to area (def: 0.01)")
    parser.add_argument("--max", type=float, default=0.1,
        help="max ratio of object size relative to area (def: 0.1)")

    args = parser.parse_args() # parse the arguments

    # check for invalid numbers
    if args.number < 0 or args.area < 0 or args.min < 0 or args.max < 0 :
        parser.error("Invalid number argument.")
    if args.max > 1 or args.min > args.max :
        parser.error("Invalid ratios.")

    # run generator
    if args.type == "interval":
        generator = IntervalGenerator(args.number, args.area, args.min,
           args.max, window_size)
    elif args.type == "rectangle":
        generator = RectangleGenerator(args.number, args.area, args.min,
           args.max, window_size)
    
    if args.print:  # print results
        print(generator)

    if args.graphics:
        generator.draw()

    if args.store:
        generator.export_data()



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
        """Prepare space and initialize generation of new objects and data"""

        self.object_number = object_number
        self.area = area
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.window = window

        self.objects_dict = {}
        self.objects_count = 0

        self.win = None   # controller for graphics window

        random.seed()       # seed random number generator


    def __init__(self, input_dict, window):
        """Load parameters, objects and data from previous run"""
        
        self.object_number = input_dict['object_number']
        self.area = input_dict['area']
        self.min_ratio = input_dict['min']
        self.max_ratio = input_dict['max']
        self.window = window

        self.objects_dict = {}
        self.objects_count = 0


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


    def as_dict(self):
        """Represent generator parameters and data as dictionary."""

        dataset = {"object_number": self.object_number, "area": self.area,
            "min": self.min_ratio, "max": self.max_ratio,
            "objects": [obj.as_dict() for obj in self.objects_dict.values()]}

        return dataset


    def load_dict(self, dict):
        """Load previously generated data from JSON format."""

        print("AAA")


    def __repr__(self):
        """Convert to string."""
        s = ",\n".join(" %d: %r" % (id_, object_) # stringify dictionary
            for id_, object_ in self.objects_dict.items())        
        return("Generator(objects={%s}\n,count=%d)" % (s, self.objects_count))


class IntervalGenerator(Generator):

    """Randomly generate overlapping intervals in a defined space

    Methods:
        __init__ -- prepares the space and generates or loads the intervals
        _generate_interval -- generates a single interval

    """

    def __init__(self, object_number, area, min_ratio, max_ratio, window):
        """Prepare space and initialize generation"""
        super().__init__(object_number, area, min_ratio, max_ratio, window)

        # generate intervals and add them to the dictionary
        for i in range(0, self.object_number):
            new_object = self._generate_interval()
            self.objects_dict[new_object.id_] = new_object
            self.objects_count += 1 


    def __init__(self, input_dict, window):
        """Load parameters, objects and data from previous run"""
        super().__init__(input_dict, window)

        # load objects from file to IntervalObjects
        for interval in input_dict['objects']:

            # load single object and add it to the dictionary
            new_object = IntervalObject(interval)
            self.objects_dict[new_object.id_] = new_object
            self.objects_count += 1


    def _generate_interval(self):
        """Generate a single random interval within the space"""
        start, end = self._get_line_segment() # generate x axis

        # assign id based on count
        id_ = self.objects_count  

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


    def export_data(self):
        """Store generator parameters and results as JSON."""

        type_ = "interval"
        generator_dict = self.as_dict()
        generator_dict["type"] = type_

        # check if data storage exists and if not, create it
        if not os.path.isdir("data"):
            os.mkdir("data")

        # open file for storage, filename is timestamp
        with open("data/%s_%s.json"% (type_, datetime.now()), "w+") as file:
            
            # write pretty JSON to file
            file.write( json.dumps(generator_dict, sort_keys=True,
                indent=4, separators=(',', ': ')))



class RectangleGenerator(Generator):

    """Randomly generate overlapping rectangles in a defined space

    Methods:
        __init__ -- prepares the space and generates or loads the rectangles
        _generate_rectangle -- generates a single rectangle

    """

    def __init__(self, object_number, area, min_ratio, max_ratio, window):
        """Prepare space and generate rectangles"""
        super().__init__(object_number, area, min_ratio, max_ratio, window)

        # generate rectangles and add them to the dictionary
        for i in range(0, self.object_number):
            new_object = self._generate_rectangle()
            self.objects_dict[new_object.id_] = new_object 
            self.objects_count += 1 


    def __init__(self, input_dict, window):
        """Load parameters, objects and data from previous run"""
        super().__init__(input_dict, window)

        # load objects from file to RectangleObjects
        for rectangle in input_dict['objects']:

            # load single object and add it to the dictionary
            new_object = RectangleObject(rectangle)
            self.objects_dict[new_object.id_] = new_object
            self.objects_count += 1



    def _generate_rectangle(self):
        """Generate a single random rectangle within the space"""
        x_start, x_end = self._get_line_segment() # generate x axis
        y_start, y_end = self._get_line_segment() # generate y axis
        
        # assign id based on count
        id_ = self.objects_count  

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


    def export_data(self):
        """Store generator parameters and results as JSON."""

        type_ = "rectangle"
        generator_dict = self.as_dict()
        generator_dict["type"] = type_

        # check if data storage exists and if not, create it
        if not os.path.isdir("data"):
            os.mkdir("data")

        # open file for storage, filename is timestamp
        with open("data/%s_%s.json"% (type_, datetime.now()), "w+") as file:
            
            # write pretty JSON to file
            file.write( json.dumps(generator_dict, sort_keys=True,
                indent=4, separators=(',', ': ')))

        

if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()