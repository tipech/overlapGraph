#!/usr/bin/env python

"""
Regions Collection

This script implements the RegionSet class, a data class that represents a
collection of Regions dataset. Provides methods for generating new datasets,
and loading from or saving to a file, in the JSON or CSV file formats. This
collection of Regions is then passed to the Intersection Graph construction
algorithm.

Classes:
- RegionSet
"""

from dataclasses import asdict, astuple, dataclass
from typing import Any, Dict, Iterable, Iterator, List, Union
from uuid import uuid4

from sources.datastructs.datasets.ioable import IOable
from sources.datastructs.datasets.timeline import EventKind
from sources.datastructs.shapes.interval import Interval
from sources.datastructs.shapes.region import Region, RegionPair
from sources.helpers.base26 import to_base26
from sources.helpers.randoms import RandomFn, Randoms

try: # cyclic codependency
  from sources.datastructs.datasets.timeline import Timeline
except ImportError:
  pass


@dataclass
class RegionSet(Iterable[Region], IOable):
  """
  Data class that represents a collection of Regions dataset.
  Provides methods for generating new datasets, and loading from or
  saving to a file, in the JSON or CSV file formats.

  Attributes:
    id:         The unique identifier for this Region.
    dimension:  The number of dimensions (dimensionality).
    regions:    The collection of Regions.
    bounds:     The bounding Region that must enclose
                all Regions in this collection.
                Or None, for no outer bounding Region.

  Properties:
    size:       The number of Regions in this collection.
    minbound:   The computed minimum Region that encloses
                all Regions in this collection within it.
    timeline:   Timeline instance for this RegionSet.

  Methods:
    Special:        __init__, __getitem__,
                    __contains__, __iter__
    Instance:       add, get, filter, overlaps
    Class Methods:  from_random, from_dict

  Inherited from IOable:
    Methods:        to_output
    Class Methods:  from_text, from_source
      Overridden:   to_object, from_object
  """
  id: str
  dimension: int
  bounds: Region
  regions: List[Region]

  def __init__(self, id: str = '', bounds: Region = None, dimension: int = 1):
    """
    Initialize a new Regions collection dataset, with the given id, the
    specified dimensionality, and the outer bounding Region that all Regions
    within this collection must be enclosed in. If bounds is None, no outer
    bounding Region, dimension must be specified or defaults to 1. If bounds
    is not None, dimension is computed based on the bounds dimensionality.
    Initialize an empty list of Regions to be populated.

    Args:
      id:
        The unique identifier for this RegionSet.
        Randonly generated with UUID v4, if not provided.
      bounds:
        The outer bounding Region that all Regions
        within this collection must be enclosed in.
        Can be None, for no outer bounding Region.
      dimension:
        The number of dimensions (dimensionality).
    """
    if bounds != None:
      assert isinstance(bounds, Region)
      dimension = bounds.dimension

    assert isinstance(dimension, int) and dimension > 0

    self.id = id if len(id) > 0 else str(uuid4())
    self.dimension = dimension
    self.regions = []
    self.bounds = bounds

  ### Properties: Getters

  @property
  def _instance_invariant(self) -> bool:
    """
    Invariant:
    - All items in self.regions are:
      - Instances of Region
      - Have same dimension as self.dimension
      - Are enclosed by bounds if not None

    Returns:
      True: If instance invariant holds
      False: Otherwise.
    """
    return all([all([isinstance(r, Region),
                     r.dimension == self.dimension,
                     self.bounds == None or self.bounds.encloses(r)]) \
                for r in self.regions])

  @property
  def size(self) -> int:
    """
    Computes the number of Regions within this collection.

    Returns:
      The number of Regions in this collection.
    """
    return len(self.regions)

  @property
  def minbounds(self) -> Region:
    """
    Computes the minimum Region that encloses all member
    Regions in this collection within it.

    Returns:
      The minimum Region that encloses all Regions
      within this collection.
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

    Returns:
      A Timeline instance for this Region.
    """
    if not hasattr(self, '_timeline'):
      self._timeline = Timeline(self)

    return self._timeline

  ### Methods: Getters

  def get(self, id: str) -> Region:
    """
    Return the Region with the given ID within this collection.
    If no Region within this collection has this ID, return None.

    Args:
      id: The unique identifier corresponding to
          the Region in this collection to be
          retrieved.

    Returns:
      The retrieved Region in this collection.
      None: If no Region with given ID in this collection.
    """
    assert isinstance(id, str) and len(id) > 0

    for region in self.regions:
      if region.id == id:
        return region

    return None

  def __getitem__(self, index: Union[int,str]) -> Region:
    """
    Retrieve the Region at the given index as an int within this collection.
    Retrieve the Region with the given ID as a str within this collection.

    Is syntactic sugar for:
      region = self[index]

    Overload Method that wraps:
      self.regions.__getitem__ when index is an int.
      self.get when index is a str.

    Args:
      index:
        The index in self.regions when is an int.
        The Region ID when is a str.

    Returns:
      The retrieved Region.
    """
    return self.get(index) if isinstance(index, str) \
                           else self.regions[index]

  def __iter__(self) -> Iterator[Region]:
    """
    Return an iterator object for iterating this collection of Regions.

    Returns:
      An iterator over this collection of Regions.
    """
    return self.regions.__iter__()

  ### Methods: Insert

  def add(self, region: Region):
    """
    Append the given Region to this collection of Regions.
    The given Region must have the same dimensionality as the number of
    dimensions specified in this collection of Regions.

    Args:
      region: The Region to be appended to this
              collection of Regions.
    """
    assert isinstance(region, Region)
    assert region.dimension == self.dimension
    if self.bounds != None:
      assert self.bounds.encloses(region)

    self.regions.append(region)

  ### Methods: Queries

  def __contains__(self, value: Union[Region, str]) -> bool:
    """
    Determine if the given Region or Region ID is contained within
    this collection. Return True if this collection contains that Region,
    otherwise False.

    Is syntactic sugar for:
      value in self

    Overload Method that wraps:
      value in self.regions, when value is a str.
      value.id in self.regions, when value is a Region.

    Args:
      value:
        The Region or Region ID to test if
        exists within this RegionSet.

    Returns:
      True:   If Region exists within this RegionSet.
      False:  Otherwise.
    """
    return self.get(value.id if isinstance(value, Region) \
                             else value) != None

  def overlaps(self, dimension: int = 0) -> List[RegionPair]:
    """
    List all of overlaps between the Regions within this set.
    This is a Naive implementation for finding all overlapping Region pairs.
    Returns a list of overlapping regions, ordered based on the lower bounds
    of the Regions along the specified dimension.

    Args:
      dimension:
        The dimension on which to order the computed
        overlapping Region pairs. Ordered based on the
        lower bounds of the Regions.

    Returns:
      A List of all pairwise overlaps between the
      Regions within this collection of Regions.
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

  def filter(self, bounds: Region) -> 'RegionSet':
    """
    Returns a new filtered RegionSet with the only the Regions
    within the given, more restricted Region bounds.

    Args:
      bounds:
        The Region that will enclose all Regions in
        new filtered RegionSet. Must be enclosed by
        self.bounds, more restrictive.

    Returns:
      The newly, created filtered RegionSet.
    """
    assert bounds.dimension == self.dimension
    if self.bounds != None:
      assert self.bounds.encloses(bounds)

    regionset = RegionSet(bounds = bounds)
    for region in self.regions:
      if bounds.encloses(region):
        regionset.add(region)

    return regionset

  ## CLass Methods: Generators

  @classmethod
  def from_random(cls, nregions: int, bounds: Region,
                       id: str = '', base26_ids: bool = True,
                       **kwargs) -> 'RegionSet':
    """
    Construct a new RegionSet with N randomly generated Regions. All randomly
    generated Regions must be enclosed by the given bounding Region. All
    subregions must have the same number of dimensions as the bounding Region.

    Args:
      nregions:   The number of Regions to be generated.
      bounds:     The bounding Region that all randomly
                  generated Regions must be enclosed by.
      id:         The unique identifier for this RegionSet.
      base26_ids: Whether or not the randonly generated
                  Regions will be assign numeric IDs,
                  encoded in Base26 (A - Z).
      kwargs:     Additional arguments passed through to
                  Region.from_intervals.

    Returns:
      The newly generated RegionSet.
    """
    assert isinstance(nregions, int) and nregions > 0

    regionset = cls(id, bounds)
    regions = bounds.random_regions(nregions, **kwargs)
    for n, region in enumerate(regions):
      if base26_ids:
        region.id = to_base26(n + 1)
      regionset.add(region)

    return regionset

  ### Class Methods: (De)serialization

  @classmethod
  def to_object(cls, object: 'RegionSet', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given RegionSet object
    that can be converted or serialized as the specified data format: 'json'.
    Additional arguments passed via kwargs are used to customize and tweak the
    object generation process.

    Args:
      object: The Interval convert to an object.
      format: The targetted output format type.
      kwargs: Additional arguments or options to customize
              and tweak the object generation process.

    kwargs:
      compact:
        Boolean flag for whether or not the data
        representation of the output JSON is a compact,
        abbreviated representation or the full data
        representation with all fields.

    Returns:
      The generated object.
    """
    assert isinstance(object, RegionSet)

    fieldnames = ['id', 'dimension', 'size', 'bounds', 'regions']

    if 'compact' in kwargs and kwargs['compact']:
      return dict(map(lambda f: (f, getattr(object, f)), fieldnames))
    else:
      return asdict(object)

  @classmethod
  def from_dict(cls, object: Dict, id: str = '') -> 'RegionSet':
    """
    Construct a new set of Region from the conversion of the given Dict.
    The Dict must contains one of the following combinations of fields:

    - regions   (List[Region-equivalent]) and
      bounds    (Region-equivalent)
    - regions   (List[Region-equivalent]) and
      dimension (int)

    Note:
    - Region-equivalent means parseable by
      Region.from_object.

    Args:
      object:
        The Dict to be converted to a RegionSet
      id:
        The unique identifier for this RegionSet
        Randonly generated with UUID v4, if not provided.

    Returns:
      The newly constructed RegionSet.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
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

    # resolve backlinks amongst the set of Regions
    for region in regionset:
      if 'intersect_' in region.data:
        assert all([r in regionset for r in region.data['intersect_']])
        region.data['intersect'] = list(map(lambda r: regionset[r], region.data['intersect_']))
        del region.data['intersect_']
      if 'union_' in region.data:
        assert all([r in regionset for r in region.data['union_']])
        region.data['union'] = list(map(lambda r: regionset[r], region.data['union_']))
        del region.data['union_']

    return regionset

  @classmethod
  def from_object(cls, object: Any, id: str = '') -> 'RegionSet':
    """
    Construct a new Region from the conversion of the given object.
    The object must contains one of the following representations:

    - A Dict that is parseable by RegionSet.from_dict.
    - A List of objects that are parseable by
      Region.from_object.

    Args:
      object:
        The object to be converted to a RegionSet.
      id:
        The unique identifier for this RegionSet.
        Randonly generated with UUID v4, if not provided.

    Returns:
      The newly constructed RegionSet.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
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
