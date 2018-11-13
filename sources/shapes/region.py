#!/usr/bin/env python

#
# region.py - Region class
#
# This script implements the Region class, a data class that defines a
# multidimensional region, with an upper and a lower vertex. Each region
# has a defined dimensionality. Provides methods for determining if there
# is an overlap between two regions and what the difference between the two
# regions is.
#
from dataclasses import dataclass, field, astuple
from functools import reduce
from typing import List
from uuid import uuid4
from .interval import Interval

@dataclass
class Region:
  """
  Dataclass that defines a multidimensional region, with an upper and a
  lower vertex. Each region has a defined dimensionality. Provides methods
  for determining if there is an overlap between two regions and what the
  difference between the two regions is.

  Properties: id, lower, upper, dimension, dimensions
  Computed Properties: lengths, midpoint, size
  Methods: __getitem__, contains, __contains__, __eq__, overlaps, difference
  Class Methods: from_intervals
  """
  id: str
  lower: List[float]
  upper: List[float]
  dimension: int = field(repr=False)
  dimensions: List[Interval] = field(repr=False)

  def __init__(self, lower: List[float], upper: List[float], dimension: int = 0, id: str = ''):
    """
    Initialize a new Region, with the lower and upper bounding vertices.
    If dimension is specified, the lower and upper vertices must match that number of
    dimensions (dimensionality), otherwise computes the dimension from the lower and
    upper vertices, which must have matching number of dimensions.
    If id is specified, sets it as the unique identifier for this Region,
    otherwise generates a random identifier, UUID v4.
    Generates the dimensions (list of Intervals) from the lower and upper vertices.
    If lower vertex has values greater than its corresponding upper values,
    swaps the lower and upper values.

    :param lower:
    :param upper:
    :param dimension:
    :param id:
    """
    if len(id) == 0:
      id = str(uuid4())
    if dimension <= 0:
      dimension = len(lower)

    assert len(id) > 0
    assert isinstance(lower, List) and isinstance(upper, List)
    assert dimension > 0 and len(lower) == len(upper) == dimension

    self.id = id
    self.dimension = dimension
    self.dimensions = [Interval(*i) for i in zip(lower, upper)]
    self.lower = [d.lower for d in self.dimensions]
    self.upper = [d.upper for d in self.dimensions]

  @property
  def _instance_invariant(self) -> bool:
    return all([
      isinstance(self.lower, List),
      isinstance(self.upper, List),
      isinstance(self.dimensions, List),
      self.dimension > 0,
      self.dimension == len(self.lower) == len(self.upper),
      all([isinstance(d, Interval) for d in self.dimensions]),
      all([self.lower[i] <= self.upper[i] for i in range(self.dimension)])
    ])

  @property
  def lengths(self) -> List[float]:
    """The distances between the lower and upper bounding vertices on each axes."""
    return [d.length for d in self.dimensions]

  @property
  def midpoint(self) -> List[float]:
    """The point equal distance between the lower and upper bounding vertices."""
    return [d.midpoint for d in self.dimensions]

  @property
  def size(self) -> float:
    """The magnitude size of the region; length, area, volume.
       Computed by multiply all the dimensional lengths (sides)
       together."""
    return reduce(lambda x, y: x * y, self.lengths)

  def __getitem__(self, dimension: int) -> Interval:
    """
    Given a dimension (index), returns the Interval for that dimension.
    Syntactic sugar: self[dimension] -> Interval

    :param dimension:
    """
    return self.dimensions[dimension]

  def contains(self, point: List[float], inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the point lies within the lower and upper bounding vertices.
    If inc_lower is True, includes the lower vertex, otherwise excludes lower vertex.
    If inc_upper is True, includes the upper vertex, otherwise excludes upper vertex.
    Return True if point lies within the lower and upper bounding vertices, otherwise False.

    :param point:
    :param inc_lower:
    :param inc_upper:
    """
    assert self.dimension == len(point)
    assert all([isinstance(x, float) for x in point])

    return all([d.contains(point[i], inc_lower, inc_upper) for i, d in enumerate(self.dimensions)])

  def __contains__(self, point: List[float]) -> bool:
    """
    Determine if the point lies within the lower and upper bounding vertices (inclusively).
    Return True if point lies within the lower and upper bounding vertices, otherwise False.
    Same as: self.contains(point, inc_lower = True, inc_upper = True)
    Syntactic Sugar: point in self

    :param point:
    """
    return self.contains(point)

  def __eq__(self, that: 'Region') -> bool:
    """
    Determine if the given Region equals to this Region.
    If the two Region have the same dimensions, then they are equal,
    otherwise they do not equal. Return True if the two Regions are
    equal, otherwise False. Syntactic Sugar: self == that

    :param that:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    return all([d == that[i] for i, d in enumerate(self.dimensions)])

  def overlaps(self, that: 'Region') -> bool:
    """
    Determine if the given Region overlaps with this Region.
    If the Regions are equal, exact same lower and upper bounding vertices, then overlaps.
    If the Regions are adjacent, then not overlapping. To be overlapping, one Region must
    contains the other's lower or upper bounding vertices. As long as all corresponding
    Intervals for each dimension overlap in both Region, then the Regions are overlapping.
    Return True if given Region overlaps with this Region, otherwise False.

    Overlapping:

    - |--------------|          -         |--------------|
      |      |-------|------|     |-------|------|       |
      |<- Region A ->|      |     |       |<- Region B ->|
      |      |<- Region B ->|     |<- Region A ->|       |
      |------|-------|      |     |       |------|-------|
             |--------------|     |--------------|

    - |--------------------|    - |--------------------|
      |  |--------------|  |      |  |--------------|  |
      |<-|-- Region A --|->|      |<-|-- Region A --|->|
      |  |<- Region B ->|  |      |  |<- Region B ->|  |
      |--|--------------|--|      |  |--------------|  |
         |--------------|         |--------------------|

    -        |--------------|   - |==============|
     |-------|------|       |     |              |
     |       |<- Region B ->|     |<- Region A ->|
     |<- Region A ->|       |     |<- Region B ->|
     |-------|------|       |     |              |
             |--------------|     |==============|

    Not Overlapping:

    - |--------------||--------------|
      |<- Region A ->||<- Region B ->|
      |--------------||--------------|

    - |--------------|
      |<- Region A ->||--------------|
      |--------------||<- Region B ->|
                      |--------------|

    :param that:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    return all([d.overlaps(that[i]) for i, d in enumerate(self.dimensions)])

  def difference(self, that: 'Region') -> 'Region':
    """
    Compute the overlapping Region between this Region and the given Region.
    Return the overlapping Region or None if the Regions do not overlap.

    - |---Region A---|          -        |---Region B---|
      |      |---Region B---|     |---Region A---|      |
      |      |#######|      |     |      |#######|      |
      |      |#######|      |     |      |#######|      |
      |------|-------|      |     |      |------ |------|
             |--------------|     |--------------|

    - |------Region A------|    - |------Region A------|
      |  |---Region B---|  |      |  |---Region B---|  |
      |  |##############|  |      |  |##############|  |
      |  |##############|  |      |  |##############|  |
      |--|--------------|--|      |  |--------------|  |
         |--------------|         |--------------------|

    -        |---Region B---|   - |===Region A===|
     |---Region A---|       |     |##############|
     |       |######|       |     |##############|
     |       |######|       |     |##############|
     |-------|------|       |     |##############|
             |--------------|     |===Region B===|

    :param that:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if not self.overlaps(that):
      return None

    return Region.from_intervals([d.difference(that[i]) for i, d in enumerate(self.dimensions)])

  @classmethod
  def from_intervals(cls, dimensions: List[Interval]) -> 'Region':
    """
    Construct a new Region from the given a list of Intervals.
    Returns a Region of dimension X, for a list of Intervals of length X.

    :param dimensions:
    """
    assert isinstance(dimensions, List)
    assert all([isinstance(d, Interval) for d in dimensions])

    return cls([d.lower for d in dimensions],
               [d.upper for d in dimensions])
