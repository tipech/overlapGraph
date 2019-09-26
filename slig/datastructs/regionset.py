#!/usr/bin/env python

"""
Regions Collection

Implements the RegionSet class, a data class that represents a collection of
Regions. Provides methods for  loading from or saving to a JSON file.

Classes:
- RegionSet
"""

from collections import abc
from dataclasses import asdict, astuple, dataclass
from typing import Any, Dict, Iterable, Iterator, List, Union
from uuid import uuid4

from .ioable import IOable
from .interval import Interval
from .region import Region


@dataclass
class RegionSet(Iterable[Region], abc.Container, abc.Sized, IOable):
  """
  A collection or dataset of Regions.

  Provides methods for generating new datasets, and loading from or
  saving to a file, in the JSON or CSV file formats.

  Extends:
    Iterable[Region]
    IOable
    abc.Container
    abc.Sized

  Attributes:
    id:         The unique identifier for this Region.
    dimension:  The number of dimensions (dimensionality).
    regions:    The collection of Regions.
    bounds:     The bounding Region that must enclose
                all Regions in this collection.
                Or None, for no outer bounding Region.
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

  def keys(self) -> Iterator[Region]:
    """
    Return an Iterator of Region unique identifiers, for
    iterating over this collection of Regions.

    Returns:
      An Iterator over this collection of Regions,
      as Region unique identifiers.
    """
    for region in self.regions:
      yield region.id

  def items(self) -> Iterator[Region]:
    """
    Return an Iterator of tuples of Region ID and Region pairs, for
    iterating over this collection of Regions.

    Returns:
      An Iterator over this collection of Regions,
      as tuples of Region ID and Region pairs.
    """
    for region in self.regions:
      yield (region.id, region)

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

  def streamadd(self, regions: Iterable[Region]):
    """
    Add all of the Regions returned from the Iterable.
    The given Regions must have the same dimensionality as the number of
    dimensions specified in this collection of Regions.

    Args:
      regions:  The Iterable of Regions to be appended
                to this collection of Regions.
    """
    for region in regions:
      self.add(region)

  ### Methods: Clone

  def __copy__(self) -> 'RegionSet':
    """
    Shallow clone this collection of Regions and
    returns the copied collection of Regions.

    Returns:
      The newly, constructed shallow copy of
      this collection of the Regions.
    """
    bounds  = self.bounds.copy() if self.bounds else None
    regions = RegionSet(bounds=bounds, dimension=self.dimension)
    regions.regions = self.regions.copy()
    return regions

  def copy(self) -> 'RegionSet':
    """
    Shallow clone this collection of Regions and
    returns the copied collection of Regions.

    Alias for:
      self.__copy__()

    Returns:
      The newly, constructed shallow copy of
      this collection of the Regions.
    """
    return self.__copy__()

  def __deepcopy__(self, memo: Dict = {}) -> 'RegionSet':
    """
    Deep clone this collection of Regions and
    returns the copied collection of Regions.

    Args:
      memo: The dictionary of objects already copied
            during the current copying pass.

    Returns:
      The newly, constructed deep copy of
      this collection of the Regions.
    """
    bounds  = self.bounds.deepcopy(memo) if self.bounds else None
    regions = RegionSet(bounds=bounds, dimension=self.dimension)
    regions.streamadd([r.deepcopy(memo) for r in self.regions])
    return regions

  def deepcopy(self, memo: Dict = {}) -> 'RegionSet':
    """
    Deep clone this collection of Regions and
    returns the copied collection of Regions.

    Alias for:
      self.__deepcopy__(memo)

    Args:
      memo: The dictionary of objects already copied
            during the current copying pass.

    Returns:
      The newly, constructed deep copy of
      this collection of the Regions.
    """
    return self.__deepcopy__(memo)


  def merge(self, other: 'RegionSet'):
    """
    Merge this Regionset to another Regionset.

    Args:
      other: The regionset to be merged with.

    Returns:
      The merged Regionset.
    """
    
    assert(other.dimension == self.dimension)

    for region in other.regions:
      self.add(region)


  ### Methods: Shuffle


  ### Methods: Queries

  def __len__(self) -> int:
    """
    Computes the number of Regions within this collection.

    Returns:
      The number of Regions in this collection.
    """
    return len(self.regions)

  def __contains__(self, value: Union[Region,str]) -> bool:
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


  def subset(self, subset: List[str]) -> 'RegionSet':
    """
    Returns a new subsetted RegionSet with the only the Regions
    within the given, more restricted Regions subset.

    Args:
      subset:
        The list of included Regions or Region
        unique identifiers.

    Returns:
      The newly, created subsetted RegionSet.
    """
    assert isinstance(subset, List)
    assert all([r in self for r in subset])

    regionset = RegionSet(bounds=self.bounds, dimension=self.dimension)

    for region in subset:
      regionset.add(region if isinstance(region, Region) else self[region])

    return regionset

  ### Methods: (De)serialization

  def to_dict(self) -> Dict:
    """
    Converts this object to a dictionary representation.

    Returns:
      The generated object.
    """
    return asdict(self)

  @classmethod
  def from_dict(cls, object: Dict, id: str = '', refset: 'RegionSet' = None) -> 'RegionSet':
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
      refset:
        A RegionSet to reference Regions from when
        rematerializing backlinks to Regions. For use
        in resulting RegionSet or subsets.

    Returns:
      The newly constructed RegionSet.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
    """
    assert isinstance(object, Dict)
    assert 'regions' in object and isinstance(object['regions'], List)

    def resolve_region(r: str) -> Region:
      if r in regionset:
        return regionset[r]
      elif isinstance(refset, RegionSet) and r in refset:
        return refset[r]
      else:
        return None

    id = object.get('id', id)

    if 'length' in object:
      assert isinstance(object['length'], int) and 0 < object['length']
      assert len(object['regions']) == object['length']

    if 'bounds' in object and object['bounds'] != None:
      regionset = cls(id, bounds=Region.from_object(object['bounds']))
    elif 'dimension' in object:
      assert isinstance(object['dimension'], int) and 0 < object['dimension']
      regionset = cls(id, dimension=object['dimension'])
    else:
      raise ValueError('Unrecognized RegionSet representation')

    for region in object['regions']:
      regionset.add(Region.from_object(region))

    if isinstance(refset, RegionSet):
      assert regionset.dimension == refset.dimension

    # resolve backlinks amongst the set of Regions
    for region in regionset:
      for field in ['intersect', 'union']:
        if field in region:
          resolved = [resolve_region(r) for r in region[field]]
          assert all(resolved)
          region[field] = resolved

    return regionset

  @classmethod
  def from_object(cls, object: Any, **kwargs) -> 'RegionSet':
    """
    Construct a new Region from the conversion of the given object.
    The object must contains one of the following representations:

    - A Dict that is parseable by RegionSet.from_dict.
    - A List of objects that are parseable by
      Region.from_object.

    Args:
      object:
        The object to be converted to a RegionSet.
      kwargs:
        Additional arguments to be passed to
        RegionSet.from_dict.

    Returns:
      The newly constructed RegionSet.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
    """
    if isinstance(object, Dict):
      return cls.from_dict(object, **kwargs)
    elif isinstance(object, List):
      regions = list(map(Region.from_object, object))
      dimension = regions[0].dimension
      assert all([r.dimension == dimension for r in regions])
      return cls.from_dict({'regions': regions, 'dimension': dimension}, **kwargs)
    else:
      raise ValueError('Unrecognized RegionSet representation')
