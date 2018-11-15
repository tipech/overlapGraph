#!/usr/bin/env python

#
# generators/regionset.py - Regions Collection
#
# This script implements the RegionSet class, a data class
# that represents a collection of Regions dataset. Provides
# methods for generating new datasets, and loading from or
# saving to a file, in the JSON or CSV file formats. This
# collection of Regions is then passed to the Intersection
# Graph construction algorithm.
#
from dataclasses import dataclass
from typing import List, Union, Iterable, Iterator
from uuid import uuid4
from ..shapes.region import Region
from .randoms import Randoms, RandomFn

@dataclass
class RegionSet(Iterable[Region]):
  """
  Data class that represents a collection of Regions dataset.
  Provides methods for generating new datasets, and loading from or
  saving to a file, in the JSON or CSV file formats.

  Properties:           name, dimension, regions
  Computed Properties:  size, bound
  Special Methods:      __init__, __getitem__, __contains__, __iter__
  Methods:              add, get
  """
  id: str
  dimension: int
  regions: List[Region]
  bounds: Region

  def __init__(self, id: str = '', bounds: Region = None, dimension: int = 1):
    """
    Initialize a new Regions collection dataset, with the given
    id, the specified dimensionality, and the outer bounding Region 
    that all Regions within this collection must be enclosed in.
    If bounds is None, no outer bounding Region, dimension must be
    specified or defaults to 1. If bounds is not None, dimension is
    computed based on the bounds dimensionality. Initialize an empty
    list of Regions to be populated.

    :param id:
    :param bounds:
    :param dimension:
    """
    if bounds != None:
      assert isinstance(bounds, Region)
      dimension = bounds.dimension

    assert isinstance(dimension, int) and dimension > 0

    self.id = id if len(id) > 0 else str(uuid4())
    self.dimension = dimension
    self.regions = []
    self.bounds = bounds

  @property
  def _instance_invariant(self) -> bool:
    return all([all([isinstance(r, Region),
                     r.dimension == self.dimension,
                     self.bounds == None or self.bounds.encloses(r)]) \
                for r in self.regions])

  @property
  def size(self) -> int:
    """The number of Regions within this collection."""
    return len(self.regions)

  @property
  def minbounds(self) -> Region:
    """
    The computed minimum Region that encloses all member 
    Regions in this collection within it.
    """
    assert self._instance_invariant

    bound = None
    for region in self.regions:
      bound = region if bound == None \
                     else bound.union(region)

    return bound

  def get(self, id: str) -> Region:
    """
    Return the Region with the given ID within this collection.
    If no Region within this collection has this ID, return None.

    :param id:
    """
    assert isinstance(id, str) and len(id) > 0

    for region in self.regions:
      if region.id == id:
        return region

    return None

  def __getitem__(self, index: Union[int,str]) -> Region:
    """
    For index: int
      Return the Region at the given index within this collection.
    For index: str
      Return the Region with the given ID within this collection.

    :param index:
    """
    return self.get(index) if isinstance(index, str) \
                           else self.regions[index]

  def __contains__(self, value: Union[Region, str]) -> bool:
    """
    For Type value: Region
      Determine if the given Region is contained within this collection.
      Return True if this collection contains that Region, otherwise False.
    For Type value: str
      Determine if the given Region ID is contained within this collection.
      Return True if this collection contains a Region with that ID,
      otherwise False.

    :param value:
    """
    return self.get(value.id if isinstance(value, Region) \
                             else value) != None

  def __iter__(self) -> Iterator[Region]:
    """Return an iterator object for iterating this collection of Regions."""
    return self.regions.__iter__()

  def add(self, region: Region):
    """
    Append the given Region to this collection of Regions.
    The given Region must have the same dimensionality as the number of
    dimensions specified in this collection of Regions.

    :param region:
    """
    assert isinstance(region, Region)
    assert region.dimension == self.dimension
    if self.bounds != None:
      assert self.bounds.encloses(region)

    self.regions.append(region)
