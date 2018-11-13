#!/usr/bin/env python

#
# interval.py - Interval class
#
# This script implements the Interval class, a data class that defines
# lower and upper bounding values for an interval. Are the building blocks for
# representing multi-dimensional regions and computing for overlap between
# those regions. Provides methods for determining if there is an overlap
# between two intervals and what the difference interval between the two
# intervals is.
#
from dataclasses import dataclass

@dataclass
class Interval:
  """
  Dataclass that defines the lower and upper bounding values for an interval.
  Building block for representing multi-dimensional regions and computing
  for overlap between those regions. Provides methods for determining if there
  is an overlap between two intervals and what the intersection length between the
  two intervals is.

  Properties: lower, upper
  Computed Properties: length, midpoint
  Methods: contains, overlaps, difference
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

  def __contains__(self, value: float) -> bool:
    """
    Determine if the value lies between the lower and upper bounding values (inclusively).
    Return True if values lies between the lower and upper bounding values, otherwise False.
    Same as: self.contains(value, inc_lower = True, inc_upper = True)
    Syntactic Sugar: value in self

    :param value:
    """
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
