#!/usr/bin/env python

"""
Interval Data Class

This script implements the Interval class, a data class that defines
lower and upper bounding values for an interval. Are the building blocks for
representing multi-dimensional regions and computing for overlap between
those regions. Provides methods for determining if there is an overlap
between two intervals, what the intersection interval between the two
intervals is, what the union interval between the two intervals is,
randomly generate intervals, and randomly choose values within an interval.
"""

from dataclasses import asdict, astuple, dataclass
from functools import reduce
from numbers import Real
from typing import Any, Callable, Dict, List, Tuple, Union

from numpy import floor

from sources.datastructs.datasets.ioable import IOable
from sources.helpers.randoms import NDArray, RandomFn, Randoms


@dataclass(order = True)
class Interval(IOable):
  """
  Dataclass that defines the lower and upper bounding values for an interval.
  Building block for representing multi-dimensional regions and computing
  for overlap between those regions. Provides methods for determining if there
  is an overlap between two intervals, what the intersection length between the
  two intervals is, what the union interval between the two intervals is,
  and randomly generate intervals.

  Properties:           lower, upper
  Computed Properties:  length, midpoint
  Special Methods:      __init__, __setattr__, __contains__
  Methods:              assign, contains, encloses, overlaps, intersect,
                        union, random_values, random_intervals
  Class Methods:        from_intersect, from_union

  Inherited from IOable:
    Methods:            to_output
    Class Methods:      from_text, from_source
      Overridden:       to_object, from_object
  """
  lower: float
  upper: float

  def __init__(self, lower, upper):
    """
    Initialize a new Interval, with the lower and upper bounding values.
    Converts input values to floating point numbers, and assigns
    the float value to the lower and upper fields. If lower is greater
    than upper, swaps the lower and upper values.

    :param lower:
    :param upper:
    """
    self.assign(float(lower), float(upper))

  @property
  def _instance_invariant(self) -> bool:
    return all([isinstance(self.lower, Real),
                isinstance(self.upper, Real),
                self.lower <= self.upper])

  @property
  def length(self) -> float:
    """The distance between the lower and upper bounding values."""
    return abs(self.upper - self.lower)

  @property
  def midpoint(self) -> float:
    """The value equal distance between the lower and upper bounding values."""
    return (self.lower + self.upper) / 2

  def __setattr__(self, name, value):
    """
    Called when an attribute assignment is attempted. This is called instead 
    of the normal mechanism. name is the attribute name, value is the value 
    to be assigned to it.
    
    Ensures that the lower and upper bounding values satisfy the object
    invariant: lower <= upper, the lower and upper bounding values cannot be 
    modified directly after this Interval is initialized. If the lower or upper
    bounding values are attempted to be set, raises an exception. This effectively
    prevents this Interval from being mutated into an invalid state. To mutate this
    Interval, call the assign() method with both lower and upper bounding values
    instead.

    :param name:
    :param value:    
    """
    if name == 'lower' or name == 'upper':
      raise Exception(f'Cannot set immutable "{name}" attribute')

    object.__setattr__(self, name, value)

  def assign(self, lower: Real, upper: Real):
    """
    Assign the lower and upper bounding values of this Interval.
    Converts input values to floating point numbers, and assigns
    the float value to the lower and upper fields. If lower is greater
    than upper, swaps the lower and upper values.

    :param lower:
    :param upper:
    """
    assert isinstance(lower, Real)
    assert isinstance(upper, Real)

    if lower > upper:
      object.__setattr__(self, 'lower', float(upper))
      object.__setattr__(self, 'upper', float(lower))
    else:
      object.__setattr__(self, 'lower', float(lower))
      object.__setattr__(self, 'upper', float(upper))

  def contains(self, value: float, inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the value lies between the lower and upper bounding values.
    If inc_lower is True, includes the lower value, otherwise excludes lower value.
    If inc_upper is True, includes the upper value, otherwise excludes upper value.
    Return True if values lies between the lower and upper bounding values, otherwise False.

    :param value:
    :param inc_lower:
    :param inc_upper:
    """
    assert self._instance_invariant

    gte_lower = self.lower <= value if inc_lower else self.lower < value
    lte_upper = self.upper >= value if inc_upper else self.upper > value

    return gte_lower and lte_upper

  def encloses(self, that: 'Interval', inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the interval lies within the lower and upper bounding values.
    If inc_lower is True, includes the lower value, otherwise excludes lower value.
    If inc_upper is True, includes the upper value, otherwise excludes upper value.
    Return True if interval lies within the lower and upper bounding values, otherwise False.

    :param that:
    :param inc_lower:
    :param inc_upper:
    """
    assert isinstance(that, Interval)

    return all([self.length >= that.length,
                self.contains(that.lower, inc_lower, inc_upper),
                self.contains(that.upper, inc_lower, inc_upper)])

  def __contains__(self, value: Union[float, 'Interval']) -> bool:
    """
    For Type value: float
      Determine if the value lies between the lower and upper bounding values (inclusively).
      Return True if values lies between the lower and upper bounding values, otherwise False.
      Same as: self.contains(value, inc_lower = True, inc_upper = True)
      Syntactic Sugar: value in self

    For Type value: Interval
      Determine if the interval lies between the lower and upper bounding values (inclusively).
      Return True if interval lies between the lower and upper bounding values, otherwise False.
      Same as: self.encloses(value, inc_lower = True, inc_upper = True)
      Syntactic Sugar: value in self

    :param value:
    """
    if isinstance(value, Interval):
      return self.encloses(value)
    else:
      return self.contains(value)

  def overlaps(self, that: 'Interval') -> bool:
    """
    Determine if the given Interval overlaps with this Interval.
    If the Intervals are equal, exact same lower and upper bounding values, then overlaps.
    If the Intervals are adjacent, then not overlapping.
    To be overlapping, one Interval must contains the other's lower or upper bounding value.
    Return True if given Interval overlaps with this Interval, otherwise False.

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
    - |<- Interval A ->||<- Interval B ->|
    - |<- Interval B ->||<- Interval A ->|
    - |<- Interval A ->|   |<- Interval B ->|
    - |<- Interval B ->|   |<- Interval A ->|

    :param that:
    """
    assert isinstance(that, Interval)
    assert self._instance_invariant
    assert that._instance_invariant

    if self == that:
      return True
    if self.upper <= that.lower or that.upper <= self.lower:
      return False

    # return any([that.lower in self, that.upper in self, self.lower in that, self.upper in that])
    return max(self.lower, that.lower) <= min(self.upper, that.upper)

  def intersect(self, that: 'Interval') -> 'Interval':
    """
    Compute the overlapping Interval between this Interval and the given Interval.
    Return the overlapping Interval or None if the Intervals do not overlap.

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

    :param that:
    """
    assert isinstance(that, Interval)
    assert self._instance_invariant
    assert that._instance_invariant

    if not self.overlaps(that):
      return None

    return Interval(max(self.lower, that.lower),
                    min(self.upper, that.upper))

  def union(self, that: 'Interval') -> 'Interval':
    """
    Compute the Interval that encloses both this Interval and the given Interval.
    Return the enclosing Interval.

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

    :param that:
    """
    assert isinstance(that, Interval)
    assert self._instance_invariant
    assert that._instance_invariant

    return Interval(min(self.lower, that.lower),
                    max(self.upper, that.upper))

  def random_values(self, nvalues: int = 1, randomng: RandomFn = Randoms.uniform()) -> NDArray:
    """
    Randomly draw N samples from a given distribution or random
    number generation function. Samples are drawn over the interval
    [lower, upper) specified by this Interval. The given size N specifies
    the number of values to output. The default nvalues is 1; a single value
    is returned. Otherwise, a list with the specified number of samples
    are drawn.

    The default behavior is that samples are uniformly distributed.
    In other words, any value within the given interval is equally
    likely to be drawn by uniform. Other distribution or random
    number generation functions can be substituted via the `randomng`
    parameter.

    :param nvalues:
    :param randomng:
    """
    assert isinstance(nvalues, int) and nvalues > 0
    assert isinstance(randomng, Callable)

    return randomng(nvalues, self.lower, self.upper)

  def random_intervals(self, nintervals: int = 1, sizepc_range: 'Interval' = None,
                             posnrng: RandomFn = Randoms.uniform(),
                             sizerng: RandomFn = Randoms.uniform(),
                             precision: int = None) -> List['Interval']:
    """
    Randomly generate N Intervals within this Interval, each with a random size
    as a percentage of the total Interval length, bounded by the given size
    percentage Interval (enclosed by Interval(0, 1)). The default distributions
    for choosing the position of the Interval and its size percentage are uniform
    distributions, but can be substituted for other distribution or random number
    generation functions via the `posnrng` and `sizerng` parameter. If precision is
    given, return the randomly generated Intervals where the lower and upper
    bounding values are rounded/truncated to the specified precision (number of
    digits after the decimal point). If precision is None, the lower and upper
    bounding values are of arbitrary precision.

    :param nintervals:
    :param sizepc_range:
    :param posnrng:
    :param sizerng:
    :param precision:
    """
    if sizepc_range == None:
      sizepc_range = Interval(0, 1)
    if precision != None:
      assert isinstance(precision, int)

    assert isinstance(sizepc_range, Interval) and Interval(0, 1).encloses(sizepc_range)
    assert isinstance(posnrng, Callable) and isinstance(sizerng, Callable)

    intervals = []
    positions = self.random_values(nintervals, posnrng)
    lengths   = [s * self.length for s in sizepc_range.random_values(nintervals, sizerng)]

    for i in range(nintervals):
      length = lengths[i]
      position = positions[i]
      lower = position if position <= self.midpoint else max(position - length, self.lower)
      upper = min(lower + length, self.upper)
      if precision != None:
        lower = round(lower, precision)
        upper = round(upper, precision)
      intervals.append(Interval(lower, upper))

    return intervals

  @classmethod
  def from_intersect(cls, intervals: List['Interval']) -> Union['Interval', None]:
    """
    Construct a new Interval from the intersection of the given list of
    Intervals. If not all the Intervals intersect, return None, otherwise
    return the Interval that intersects with all of the given Intervals.

    :param intervals:
    """
    assert isinstance(intervals, List) and len(intervals) > 1
    assert all([isinstance(interval, Interval) for interval in intervals])

    def intersect(a: Interval, b: Interval) -> Interval:
      assert a != None and b != None
      assert a.overlaps(b)      
      return a.intersect(b)

    try:
      return reduce(intersect, intervals)
    except AssertionError:
      return None

  @classmethod
  def from_union(cls, intervals: List['Interval']) -> 'Interval':
    """
    Construct a new Interval from the union of the given list of
    Intervals. Return the Interval that encloses all of the given
    Intervals.

    :param intervals:
    """
    assert isinstance(intervals, List) and len(intervals) > 1
    assert all([isinstance(interval, Interval) for interval in intervals])

    return reduce(lambda a, b: a.union(b), intervals)

  @classmethod
  def to_object(cls, object: 'Interval', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given Interval object that
    can be converted or serialized as the specified data format: 'json'. Additional
    arguments passed via kwargs are used to the customize and tweak the object
    generation process. kwargs arguments:

    - 'compact': True or False, which specifies whether or not
      the data representation of the output JSON is a compact, abbreviated
      representation or the full data representation with all fields.

    :param object:
    :param format:
    :param kwargs:
    """
    assert isinstance(object, Interval)

    if 'compact' in kwargs and kwargs['compact']:
      return astuple(object)
    else:
      return asdict(object)

  @classmethod
  def from_object(cls, object: Any) -> 'Interval':
    """
    Construct a new Interval from the conversion of the given
    object. The object may be a Dict, List or Tuple. If it is a
    Dict contains fields: lower and upper bounding values. If it
    is a List or Tuple contains 2 values, first for the lower bound
    and second for the upper bound. Returns the new Interval.

    :param object:
    """
    if isinstance(object, Dict):
      assert 'lower' in object and isinstance(object['lower'], Real)
      assert 'upper' in object and isinstance(object['upper'], Real)
      return Interval(**object)
    else:
      assert isinstance(object, (List, Tuple)) and len(object) == 2
      assert all([isinstance(item, Real) for item in object])
      return Interval(*object)
