"""Setup containers for overlapping objects of different shapes.

Provides several classes that describe individual types of objects relevant to
 the overlap problem.

Classes:
  RectangleObject -- rectangle objects
  IntervalObject -- interval objects

"""

class RectangleObject:
    """Hold the dimensions of a rectangle object.

    Properties:
        x1 -- X coordinate of starting corner
        y1 -- Y coordinate of starting corner
        x2 -- X coordinate of opposite corner
        y2 -- Y coordinate of opposite corner
        id_ -- id of specific object

    """

    def __init__(self, x1, y1, x2, y2, id_=None):
        """Create a rectangle from two opposite corners."""
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id_ = id_

    def get_center(self):
        """Calculate the coordinates of the recatangle's center"""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


    def __repr__(self):
        """Convert to string."""
        return ("Rectangle(id=%r,x1=%r,y1=%r,x2=%r,y2=%r)"
            % (self.id_, self.x1, self.y1, self.x2, self.y2))


class IntervalObject:
    """Hold the dimensions of an interval object.

    Properties:
        start -- coordinate of starting point
        end -- coordinate of ending point
        id_ -- id of specific object

    """

    def __init__(self, start, end, id_=None):
        """Create an interval (line segment)."""
        self.start = start
        self.end = end
        self.id_ = id_


    def get_center(self):
        """Calculate the coordinate of the interval's center"""
        return (self.start + self.end) / 2


    def __repr__(self):
        """Convert to string."""
        return ("Interval(id=%r,start=%r,end=%r)"
            % (self.id_, self.start, self.end))