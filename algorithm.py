"""Apply a version of sweep-line algorithm to overlapping shape data.

Provides sweep-line algorithms for the different shapes of the overlap problem.
Moreover, this can be executed as a script to actually run the algorithms.

Classes:


"""
import sys, argparse
from shapes import IntervalObject, RectangleObject
from generator import IntervalGenerator, RectangleGenerator
from graphics import Point, Line, Rectangle, Text, GraphWin
from pprint import pprint



def main():
    """Run an algorithm with command-line parameters."""

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Run a sweep-line algorithm on overlapping shape data.")

    # positional arguments: object type, number of objects
    parser.add_argument("type", choices=["interval", "rectangle"],
        help="type of overlapping objects")
    # parser.add_argument("number", metavar="N", type=int,
    #     help="number of generated objects")

    # # optional arguments: print results, draw results with graphics
    # parser.add_argument("-p", "--print", action="store_true",
    #     help="print results to console")
    # parser.add_argument("-g", "--graphics", action="store_true",
    #     help="display graphics and draw results")
    
    # # extra optional arguments: area size, min & max object size ratios
    # parser.add_argument("--area", type=int, default=1000,
    #     help="size of generated area (default: 1000)")
    # parser.add_argument("--min", type=float, default=0.01,
    #     help="min ratio of object size relative to area (def: 0.01)")
    # parser.add_argument("--max", type=float, default=0.1,
    #     help="max ratio of object size relative to area (def: 0.1)")

    # # check for invalid numbers
    # args = parser.parse_args()
    # if args.number < 0 or args.area < 0 or args.min < 0 or args.max < 0 :
    #     parser.error("Invalid number argument.")
    # if args.max > 1 or args.min > args.max :
    #     parser.error("Invalid ratios.")

    # # run generator
    # if args.type == "interval":
    #     generator = IntervalGenerator(args.number, args.area, args.min,
    #        args.max, 1200)
    # elif args.type == "rectangle":
    #     generator = RectangleGenerator(args.number, args.area, args.min,
    #        args.max, 1200)


