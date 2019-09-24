#!/usr/bin/env python

"""
Interval Data Class

Implements the Interval class, a data class that defines lower and upper
bounding values for an interval. Intervals are the building blocks for
representing multi-dimensional region objects.
Provides methods for determining if there is an overlap between two intervals
and what that overlap interval is.


Classes:
- Interval
"""

from dataclasses import dataclass
from functools import reduce
from numbers import Number, Real
from typing import Any, Dict, List, Union

from .ioable import IOable


@dataclass
class Interval(IOable):
  """
  The lower and upper bounding values for an interval.

  Building block for representing multi-dimensional regions and computing
  for overlap between those regions. Provides methods for determining if there
  is an overlap between two intervals and what the intersection length between
  the two intervals is.

  Attributes:
    lower, upper:
      The lower and upper bounding values.
  """
  lower: float
  upper: float

  def __init__(self, lower: Union[Number,str], upper: Union[Number,str]):
    """
    Initialize a new Interval, with the lower and upper bounding values.
    Converts input values to floating point numbers, and assigns
    the float value to the lower and upper fields. If lower is greater
    than upper, swaps the lower and upper values.

    Args:
      lower, upper:
        the lower and upper bounding values.
    """
    lower = float(lower)
    upper = float(upper)

    assert isinstance(lower, Real)
    assert isinstance(upper, Real)

    if lower > upper:
      self.lower = float(upper)
      self.upper = float(lower)
    else:
      self.lower = float(lower)
      self.upper = float(upper)



  ### Properties: Getters

  @property
  def length(self) -> float:
    """
    Compute the length of this Interval.

    Returns:
      The distance between the lower and
      upper bounding values.
    """
    return abs(self.upper - self.lower)


  @property
  def midpoint(self) -> float:
    """
    Compute the midpoint between the lower and upper bounds
    of this Interval.

    Returns:
      The value equal distance between the lower and
      upper bounding values.
    """
    return (self.lower + self.upper) / 2


  ### Methods: Clone

  def __copy__(self) -> 'Interval':
    """
    Create a shallow copy of this Interval and return it.

    Returns:
      The newly created Interval copy.
    """
    return Interval(self.lower, self.upper)


  def copy(self) -> 'Interval':
    """
    Alias for self.__copy__()
    """
    return self.__copy__()


  ### Methods: Queries

  def __eq__(self, that) -> bool:
    """
    Determine if this interval is equivalent to another.

    Args:
      that:
        The other Interval to test for equality. If for
        both intervals lower and upper values match,
        they are equal.

    Returns:
      True:   If intervals are equal.
      False:  Otherwise.
    """
    if that is None:
      return self is None

    assert isinstance(that, Interval)

    return self.lower == that.lower and self.upper == that.upper



  def contains(self, value: float, inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the value lies between the lower and upper bounding values.

    Args:
      value:
        The value to test if it lies within
        this Interval's bounds.
      inc_lower, inc_upper:
        Boolean flag for whether or not to include or
        to exclude the lower or upper bounding values
        of this Interval. If inc_lower is True, includes
        the lower bounding value, otherwise excludes it.
        Likewise, if inc_upper is True, includes the
        upper bounding value, otherwise excludes it.

    Returns:
      True:   If values lies between the lower and
              upper bounding values.
      False:  Otherwise.
    """

    gte_lower = self.lower <= value if inc_lower else self.lower < value
    lte_upper = self.upper >= value if inc_upper else self.upper > value

    return gte_lower and lte_upper


  def encloses(self, that: 'Interval', inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if that Interval lies entirely within this Interval.

    Args:
      that:
        The other Interval to test if it lies
        entirely within this Interval's bounds.
      inc_lower, inc_upper:
        Boolean flag for whether or not to include or
        to exclude the lower or upper bounding values
        of this Interval. If inc_lower is True, includes
        the lower bounding value, otherwise excludes it.
        Likewise, if inc_upper is True, includes the
        upper bounding value, otherwise excludes it.

    Returns:
      True:   If other Interval lies entirely within
              this Interval's bounds.
      False:  Otherwise.
    """
    assert isinstance(that, Interval)

    return all([self.length >= that.length,
                self.contains(that.lower, inc_lower, inc_upper),
                self.contains(that.upper, inc_lower, inc_upper)])


  def is_intersecting(self, that: 'Interval', inc_bounds = False) -> bool:
    """
    Determine if the given Interval overlaps with this Interval.
    If the intervals are exactly adjacent (one's lower is equal other's upper),
    then if they intersect or not is decided by inc_bounds flag.
    To be overlapping, one Interval must contain the other's lower or upper
    bounding value. Return True if given Interval overlaps with this Interval,
    otherwise False.

    Args:
      that:
        The other Interval to test if it overlaps
        with this Interval.
      inc_bounds:
        If intervals considered intersecting when
        lower/upper bounds are exactly equal
        (zero-length intersection)

    Returns:
      True:   If that Interval overlaps with this Interval
      False:  Otherwise.

    Examples:

      Overlapping:
      - |<---- Interval A ---->|
        |<---- Interval B ---->|
      - |<---- Interval A ---->|
            |<- Interval B ->|
      -    |<- Interval A ->|
        |<---- Interval B ---->|
      - |<- Interval A ->|
              |<- Interval B ->|
      -       |<- Interval A ->|
        |<- Interval B ->|

      Not overlapping:
      - |<- Interval A ->|   |<- Interval B ->|
      - |<- Interval B ->|   |<- Interval A ->|

      Conditionally overlapping:
      - |<- Interval A ->|<- Interval B ->|
      - |<- Interval B ->|<- Interval A ->|
    """
    assert isinstance(that, Interval)

    if self == that:
      return True

    if inc_bounds:
      return self.upper >= that.lower and that.upper >= self.lower

    return self.upper > that.lower and that.upper > self.lower


  def get_intersection(self, that: 'Interval', inc_bounds = False) -> Union['Interval', None]:
    """
    Compute the overlapping Interval between this Interval and that Interval.
    If the intervals are exactly adjacent (one's lower is equal other's upper),
    then if they intersect or not is decided by inc_bounds flag.
    Return the overlapping Interval or None if the Intervals do not overlap.

    Args:
      that:
        The other Interval which this Interval is to compute
        the overlapping Interval with.
      inc_bounds:
        If intervals considered intersecting when
        lower/upper bounds are exactly equal
        (zero-length intersection)

    Returns:
      The overlapping Interval: If the Intervals overlap.
      None: If the Intervals do not overlap.

    Examples:

      Intersects:
      - |<---- Interval A ---->|
        |<---- Interval B ---->|
        |<---- ########## ---->|
      - |<---- Interval A ---->|
            |<- Interval B ->|
            |<- ########## ->|
      -    |<- Interval A ->|
        |<---- Interval B ---->|
            |<- ######### ->|
      - |<- Interval A ->|
              |<- Interval B ->|
              |<- #### ->|
      -       |<- Interval A ->|
        |<- Interval B ->|
              |<- #### ->|
    """
    assert isinstance(that, Interval)

    if not self.is_intersecting(that, inc_bounds):
      return None

    return Interval(max(self.lower, that.lower),
                    min(self.upper, that.upper))


  def get_union(self, that: 'Interval') -> 'Interval':
    """
    Compute the Interval that encloses both this Interval and that Interval.
    Return the enclosing Interval.

    Args:
      that:
        The other Interval which this Interval is to compute
        the encloseing Interval with.

    Returns:
      The enclosing Interval.

    Examples:

      Unions:
      - |<- Interval A ->|        |<- A ->||<- B ->|
        |<- Interval B ->|        |<- B ->||<- A ->|
        |<- ########## ->|        |<- ########## ->|
      - |<--- Interval A --->|        |<- Interval A ->|
            |<- Interval B ->|    |<--- Interval B --->|
        |<- ############## ->|    |<- ############## ->|
      - |<- Interval A ->|        |<- Interval A ->|
            |<- Interval B ->|    |<- Interval B ->|
        |<- ############## ->|    |<- ############## ->|
      - |<- A ->|    |<- B ->|    |<- B ->|    |<- A ->|
        |<- ############## ->|    |<- ############## ->|
    """
    assert isinstance(that, Interval)

    return Interval(min(self.lower, that.lower),
                    max(self.upper, that.upper))


  ### Class Methods: Generators

  @classmethod
  def from_intersection(cls, intervals: List['Interval']) -> Union['Interval', None]:
    """
    Construct a new Interval from the intersection of the given list of
    Intervals. If not all the Intervals intersect, return None, otherwise
    return the Interval that intersects with all of the given Intervals.

    Args:
      intervals:
        List of Intervals to compute the intersecting
        Interval amongst.

    Returns:
      Interval that intersects with all given Intervals.
      None: If not all the Intervals intersect.
    """
    assert isinstance(intervals, List) and len(intervals) > 1
    assert all([isinstance(interval, Interval) for interval in intervals])

    def intersect(a: Interval, b: Interval) -> Interval:
      assert a != None and b != None
      assert a.is_intersecting(b)
      return a.get_intersection(b)


    try:
      return reduce(intersect, intervals)
    except AssertionError:
      return None


  @classmethod
  def from_union(cls, intervals: List['Interval']) -> 'Interval':
    """
    Construct a new Interval from the union of the given list of Intervals.
    Return the Interval that encloses all of the given Intervals.

    Args:
      intervals:
        List of Intervals to compute the union
        Interval amongst.

    Returns:
      Interval that encloses all of the given Intervals.
    """
    assert isinstance(intervals, List) and len(intervals) > 1
    assert all([isinstance(interval, Interval) for interval in intervals])

    return reduce(lambda a, b: a.get_union(b), intervals)


  ### Class Methods: (De)serialization

  def to_dict(self) -> Dict:
    """
    Generates a dict object from this Interval object that can be serialized.

    Returns:
      The generated dict.
    """

    return {'lower': self.lower, 'upper': self.upper}


  @classmethod
  def from_dict(cls, object: Dict) -> 'Interval':
    """
    Construct a new Interval from the conversion of the given Dict object with
    lower and upper bounding value fields.

    Args:
      object:
        The Dict to be converted into a new Interval instance.

    Returns:
      The newly constructed Interval.
    """
    assert isinstance(object, Dict)
    assert 'lower' in object and isinstance(object['lower'], (Real, str))
    assert 'upper' in object and isinstance(object['upper'], (Real, str))
    return Interval(**object)