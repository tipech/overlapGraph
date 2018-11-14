#!/usr/bin/env python

#
# shapes/interval.py - Interval class
#
# This script implements the Interval class, a data class that defines
# lower and upper bounding values for an interval. Are the building blocks for
# representing multi-dimensional regions and computing for overlap between
# those regions. Provides methods for determining if there is an overlap
# between two intervals and what the difference interval between the two
# intervals is.
#
from dataclasses import dataclass
from numpy import floor
from typing import List, Union, Callable
from ..generators.randoms import Randoms, RandomFn, NDArray

@dataclass
class Interval:
  """
  Dataclass that defines the lower and upper bounding values for an interval.
  Building block for representing multi-dimensional regions and computing
  for overlap between those regions. Provides methods for determining if there
  is an overlap between two intervals and what the intersection length between the
  two intervals is.

  Properties:           lower, upper
  Computed Properties:  length, midpoint
  Special Methods:      __init__, __contains__
  Methods:              contains, encloses, overlaps, difference, 
                        random_values, random_intervals
  """
  lower: float
  upper: float

  def _assign(self, lower: float, upper: float):
    self.lower = lower
    self.upper = upper

  def __init__(self, lower, upper):
    """
    Initialize a new Interval, with the lower and upper bounding values.
    Converts input values to floating point numbers, and assigns
    the float value to the lower and upper fields. If lower is greater
    than upper, swaps the lower and upper values.

    :param lower:
    :param upper:
    """
    self._assign(float(lower), float(upper))
    if self.lower > self.upper:
      self._assign(self.upper, self.lower)

  @property
  def _instance_invariant(self) -> bool:
    return all([isinstance(self.lower, float),
                isinstance(self.upper, float),
                self.lower <= self.upper])

  @property
  def length(self) -> float:
    """The distance between the lower and upper bounding values."""
    return abs(self.upper - self.lower)

  @property
  def midpoint(self) -> float:
    """The value equal distance between the lower and upper bounding values."""
    return (self.lower + self.upper) / 2

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

  def difference(self, that: 'Interval') -> 'Interval':
    """
    Compute the overlapping Interval between this Interval and the given Interval.
    Return the overlapping Interval or None if the Intervals do not overlap.

    Difference:
    - |<---- Interval A ---->|
      |<---- Interval B ---->|
      |<---- Difference ---->|
    - |<---- Interval A ---->|
          |<- Interval B ->|
          |<- Difference ->|
    -    |<- Interval A ->|
      |<---- Interval B ---->|
          |<- Difference ->|
    - |<- Interval A ->|
            |<- Interval B ->|
            |<- Diff ->|
    -       |<- Interval A ->|
      |<- Interval B ->|
            |<- Diff ->|

    :param that:
    """
    assert isinstance(that, Interval)
    assert self._instance_invariant
    assert that._instance_invariant

    if not self.overlaps(that):
      return None

    return Interval(max(self.lower, that.lower),
                    min(self.upper, that.upper))

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
                             intonly: bool = False) -> List['Interval']:
    """
    Randomly generate N Intervals within this Interval, each with a random size
    as a percentage of the total Interval length, bounded by the given size
    percentage Interval (enclosed by Interval(0, 1)). The default distributions
    for choosing the position of the Interval and its size percentage are uniform
    distributions, but can be substituted for other distribution or random number
    generation functions via the `posnrng` and `sizerng` parameter. If intonly is
    True, return the randomly generated Intervals where the lower and upper 
    bounding values are floored/truncated into integer values.

    :param nintervals:
    :param sizepc_range:
    :param posnrng:
    :param sizerng:
    :param intonly:
    """
    if sizepc_range == None:
      sizepc_range = Interval(0, 1)

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
      if intonly:
        lower = floor(lower)
        upper = floor(upper)     
      intervals.append(Interval(lower, upper))

    return intervals
