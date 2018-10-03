"""Apply a version of sweep-line algorithm to overlapping shape data.

Provides sweep-line algorithms for the different shapes of the overlap problem.
Moreover, this can be executed as a script to actually run the algorithms.

Classes:


"""
import sys, argparse, json
from shapes import IntervalObject, RectangleObject
from generator import IntervalGenerator, RectangleGenerator
from graphics import Point, Line, Rectangle, Text, GraphWin
from pprint import pprint



def main():
    """Run an algorithm with command-line parameters."""

    window_size = 1200

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Run a sweep-line algorithm on overlapping shape data.")

    
    # provide options to run with previously generated data or generate new 
    subparsers = parser.add_subparsers()
    load_parser = subparsers.add_parser('load', help="load generated data")
    gen_parser = subparsers.add_parser('generate', help="generate new data")

    # if previous data selected, get file name
    load_parser.add_argument("file", help="generated data file name")

    # optional arguments: print result graph, draw graph
    load_parser.add_argument("-p", "--print", action="store_true",
        help="print results to console")
    load_parser.add_argument("-g", "--graphics", action="store_true",
        help="display graphics and draw results")

    # else, get generator parameters: object type
    gen_parser.add_argument("type", choices=["interval", "rectangle"],
        help="type of overlapping objects")

    # optional arguments: print result graph, draw graph
    gen_parser.add_argument("-p", "--print", action="store_true",
        help="print results to console")
    gen_parser.add_argument("-g", "--graphics", action="store_true",
        help="display graphics and draw results")

    # extra optional arguments: number of objects, area, min & max size ratios
    gen_parser.add_argument("--number", metavar="N", type=int, default=20,
        help="number of generated objects")
    gen_parser.add_argument("--area", type=int, default=1000,
        help="size of generated area (default: 1000)")
    gen_parser.add_argument("--min", type=float, default=0.01,
        help="min ratio of object size relative to area (def: 0.01)")
    gen_parser.add_argument("--max", type=float, default=0.1,
        help="max ratio of object size relative to area (def: 0.1)")
    
    args = parser.parse_args() # parse the arguments
    

    if "file" in args: # if we selected to load data
        
        # try opening the data file
        try:
            with open(args.file, "r") as input_file:
                
                # parse the json data
                data = json.load(input_file)

                # depending on type, load data into generator
                if data['type'] == "interval":
                    generator = IntervalGenerator(data, window_size)
                elif data['type'] == "rectangle":
                    generator = RectangleGenerator(data, window_size)

                pprint(generator.objects_dict)

        # if error occured during file reading, print invalid argument error
        except Exception as e:
            parser.error("Problem occured during file reading: \n\t%s" % e)

    else: # if we selected to generate new data

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


        pprint(generator.objects_dict)




if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()