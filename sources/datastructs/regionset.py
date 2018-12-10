#!/usr/bin/env python

#
# datastructs/regionset.py - Regions Collection
#
# This script implements the RegionSet class, a data class
# that represents a collection of Regions dataset. Provides
# methods for generating new datasets, and loading from or
# saving to a file, in the JSON or CSV file formats. This
# collection of Regions is then passed to the Intersection
# Graph construction algorithm.
#

from dataclasses import asdict, astuple, dataclass
from typing import Any, Dict, Iterable, Iterator, List, Union
from uuid import uuid4

from ..helpers.base26 import to_base26
from ..helpers.randoms import RandomFn, Randoms
from .interval import Interval
from .ioable import IOable
from .region import Region, RegionPair
from .timeline import EventKind

try: # cyclic codependency
  from .timeline import Timeline
except ImportError:
  pass


@dataclass
class RegionSet(Iterable[Region], IOable):
  """
  Data class that represents a collection of Regions dataset.
  Provides methods for generating new datasets, and loading from or
  saving to a file, in the JSON or CSV file formats.

  Properties:           name, dimension, regions, bounds
  Computed Properties:  size, minbound, timeline
  Special Methods:      __init__, __getitem__, __contains__, __iter__
  Methods:              add, get, filter, overlaps
  Class Methods:        from_random, from_dict

  Inherited from IOable:
    Methods:            to_output
    Class Methods:      from_text, from_source
      Overridden:       to_object, from_object
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
    return Region.from_union(self.regions)

  @property
  def timeline(self) -> 'Timeline':
    """
    Return a Timeline instance binded to this RegionSet. The Timeline
    provides methods for generating sorted iterations of Events for 
    each dimension in the Regions within this RegionSet; each Region
    results in a beginning and an ending event. Each RegionSet may only
    have one Timeline instance, once created always returns the same
    instance.
    """
    if not hasattr(self, '_timeline'):
      self._timeline = Timeline(self)

    return self._timeline

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

  def filter(self, bounds: Region) -> 'RegionSet':
    """
    Returns a new filtered RegionSet with the only the Regions
    within the given, more restricted Region bounds.

    :param bounds:
    """
    assert bounds.dimension == self.dimension
    if self.bounds != None:
      assert self.bounds.encloses(bounds)

    regionset = RegionSet(bounds = bounds)
    for region in self.regions:
      if bounds.encloses(region):
        regionset.add(region)

    return regionset

  def overlaps(self, dimension: int = 0) -> List[RegionPair]:
    """
    List all of overlaps between the Regions within this set.
    This is a Naive implementation for finding all overlapping Region pairs.
    Returns a list of overlapping pairs, ordered based on the lower bounds
    of the Regions along the specified dimension.

    :param dimension:
    """
    ordered_regions = []
    for event in self.timeline.events(dimension):
      if event.kind == EventKind.Begin:
        ordered_regions.append(event.context)

    overlaps = []
    for first in ordered_regions:
      for second in ordered_regions:
        if first is second: continue
        if first[dimension].lower > second[dimension].lower: continue
        if (second, first) in overlaps: continue
        if first.overlaps(second):
          overlaps.append((first, second))

    return overlaps

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
    via the `posnrng` and `sizerng` parameter. If precision is given, return the
    randomly generated Intervals where the lower and upper bounding values are 
    rounded/truncated to the specified precision (number of digits after the
    decimal point). If precision is None, the lower and upper bounding values
    are of arbitrary precision. If base26_ids is True, the randonly generated
    Region will be assign a numeric ID, encoded in Base26 (A - Z).

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

  @classmethod
  def from_dict(cls, object: Dict, id: str = '') -> 'RegionSet':
    """
    Construct a new set of Region from the conversion of the given Dict.
    The Dict must contains one of the following combinations of fields:

    - regions (List[Region-equivalent]) and bounds (Region-equivalent)
    - regions (List[Region-equivalent]) and dimension (int)

    Region-equivalent means parseable by Region.from_object.
    If id is specified, sets it as the unique identifier for this RegionSet, otherwise
    generates a random identifier, UUID v4. If object does not have one of the above
    combinations of fields, raises ValueError. Returns the newly constructed RegionSet.

    :param object:
    :param id:
    """
    assert isinstance(object, Dict)
    assert 'regions' in object and isinstance(object['regions'], List)

    if 'id' in object:
      id = object['id']

    if 'size' in object:
      assert isinstance(object['size'], int) and 0 < object['size']
      assert len(object['regions']) == object['size']

    if 'bounds' in object and object['bounds'] != None:
      regionset = cls(id, bounds=Region.from_object(object['bounds']))
    elif 'dimension' in object:
      assert isinstance(object['dimension'], int) and 0 < object['dimension']
      regionset = cls(id, dimension=object['dimension'])
    else:
      raise ValueError('Unrecognized RegionSet representation')

    for region in object['regions']:
      regionset.add(Region.from_object(region))

    return regionset

  @classmethod
  def to_object(cls, object: 'RegionSet', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given RegionSet object that
    can be converted or serialized as the specified data format: 'json'. Additional
    arguments passed via kwargs are used to the customize and tweak the object
    generation process.

    :param object:
    :param format:
    :param kwargs:
    """
    assert isinstance(object, RegionSet)

    fieldnames = ['id', 'dimension', 'size', 'bounds', 'regions']

    if 'compact' in kwargs and kwargs['compact']:
      return dict(map(lambda f: (f, getattr(object, f)), fieldnames))
    else:
      return asdict(object)

  @classmethod
  def from_object(cls, object: Any, id: str = '') -> 'RegionSet':
    """
    Construct a new set of Region from the conversion of the given object.
    The object must contains one of the following representations:

    - A Dict that is parseable by the from_dict method.
    - A List of objects that are parseable by Region.from_object

    If id is specified, sets it as the unique identifier for this RegionSet, otherwise
    generates a random identifier, UUID v4. If object does not have one of the above
    combinations of fields, raises ValueError. Returns the newly constructed RegionSet.

    :param object:
    :param id:
    """
    if isinstance(object, Dict):
      return cls.from_dict(object, id)
    elif isinstance(object, List):
      regions = list(map(Region.from_object, object))
      dimension = regions[0].dimension
      assert all([r.dimension == dimension for r in regions])
      return cls.from_dict({'regions': regions, 'dimension': dimension}, id)
    else:
      raise ValueError('Unrecognized RegionSet representation')
