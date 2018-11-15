#!/usr/bin/env python

#
# shapes/regionset.py - Regions Collection
#
# This script implements the RegionSet class, a data class
# that represents a collection of Regions dataset. Provides
# methods for generating new datasets, and loading from or
# saving to a file, in the JSON or CSV file formats. This
# collection of Regions is then passed to the Intersection
# Graph construction algorithm.
#
from dataclasses import dataclass, asdict, astuple
from io import TextIOBase
from json import JSONEncoder
from typing import List, Union, Iterable, Iterator
from uuid import uuid4
from ..helpers.base26 import to_base26
from ..helpers.randoms import Randoms, RandomFn
from .interval import Interval
from .region import Region

@dataclass
class RegionSet(Iterable[Region]):
  """
  Data class that represents a collection of Regions dataset.
  Provides methods for generating new datasets, and loading from or
  saving to a file, in the JSON or CSV file formats.

  Properties:           name, dimension, regions, bounds
  Computed Properties:  size, minbound
  Special Methods:      __init__, __getitem__, __contains__, __iter__
  Methods:              add, get, to_json
  Class Methods:        from_random
  """
  id: str
  dimension: int
  bounds: Region
  regions: List[Region]

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

  def to_json(self, output: TextIOBase, compact: bool = False, **options):
    """
    Output this collection of Regions in the JSON serialization 
    format to the given output writable IO stream. If compact is 
    True, output abbreviated JSON data structure, otherwise output
    all fields in full.

      regionset = RegionSet.from_random(100, Region([0]*2, [100]*2))
      with open('output.csv', 'w') as f:
        regionset.to_json(f, compact = True)

    :param output:
    :param compact:
    :param options:
    """
    assert output.writable()

    regionset_fields = ['id', 'dimension', 'size', 'bounds', 'regions']
    region_fields = ['id', 'dimension', 'dimensions']

    def pick_fields(value, picks):
      return [(key, getattr(value, key)) for key in picks]

    def json_encoder(value):
      if isinstance(value, RegionSet):
        return dict(pick_fields(value, regionset_fields)) if compact else asdict(value)
      if isinstance(value, Interval):
        return astuple(value)
      if isinstance(value, Region):
        return dict(pick_fields(value, region_fields)) if compact else asdict(value)
      raise TypeError(f'{value}')

    encoder = JSONEncoder(indent = 2, default = json_encoder, **options)
    for chunk in encoder.iterencode(self):
      output.write(chunk)

  @classmethod
  def from_random(cls, nregions: int, bounds: Region, 
                       id: str = '', base26_ids: bool = True,
                       **args) -> 'RegionSet':
    """
    Construct a new RegionSet with N randomly generated Regions.
    All randomly generated Regions must be enclosed by the given bounding Region.
    Each Region has a random size as a percentage of the total bounding Region 
    dimensions, bounded by the given size percentage Region (enclosed by 
    Region([0, ...], [1, ...])). All subregions must have the same number of
    dimensions as the bounding Region. The default distributions for choosing the
    position of the Region and its size percentage are uniform distributions, but
    can be substituted for other distribution or random number generation functions
    via the `posnrng` and `sizerng` parameter. If intonly is True, return the
    randomly generated Regions where the lower and upper bounding values are
    floored/truncated into integer values. If base26_ids is True, the randonly
    generated Region will be assign a numeric ID, encoded in Base26 (A - Z).

    :param nregions:
    :param bounds:
    :param id:
    :param base26_ids:
    :param args:
    """
    assert isinstance(nregions, int) and nregions > 0

    regionset = cls(id, bounds)
    regions = bounds.random_regions(nregions, **args)
    for n, region in enumerate(regions):
      if base26_ids:
        region.id = to_base26(n + 1)
      regionset.add(region)

    return regionset
