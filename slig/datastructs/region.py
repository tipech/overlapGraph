#!/usr/bin/env python

"""
Region Data Class

Implements the Region class, a data class that defines a multidimensional
region, with an upper and a lower vertex. Each region has a defined
dimensionality. Provides methods for determining if there is an overlap
between two regions, what the intersection or union regions between the two
regions are, and randomly generate regions and points within a region.

Types:
- RegionPair
- RegionIntxn
- RegionGrp

Classes:
- Region
"""

from dataclasses import asdict, astuple, dataclass, field
from functools import reduce
from numbers import Real
from typing import Any, Callable, Dict, List, Tuple, Union
from uuid import uuid4

from .ioable import IOable
from .interval import Interval


# RegionPair    = Tuple['Region', 'Region']
# RegionIntxn   = List['Region']
# RegionGrp     = Union['Region', RegionIntxn, RegionPair]
# RegionIdPair  = Tuple[str, str]
# RegionIdIntxn = List[RegionId]
# RegionIdGrp   = Union[RegionId, RegionIdIntxn, RegionIdPair]


@dataclass
class Region(IOable):
  """
  A multidimensional region, with an upper and lower vertex.

  Each region has a defined dimensionality. The class methods for determining
  if there is an intersection/union between two regions.

  Extends:
    IOable
    abc.Container

  Attributes:
    id:         The unique identifier for this Region.
    dimension:  The number of dimensions (dimensionality).
    factors:    The Interval (bounds) for each dimension.
    data:       Additional data properties.
  """
  id: str
  dimension: int = field(repr=False)
  factors: List[Interval] = field(repr=False)
  originals: List['Region'] = field(repr=False)
  data: Dict = field(repr=False)

  def __init__(self, lower: List[float], upper: List[float],
                     originals: List[str] = [], id: str = '', **kwargs):
    """
    Initialize a new Region, with the lower and upper bounding vertices.
    Computes the dimension from the lower and upper vertices, which must have
    matching number of dimensions. If id is specified, sets it as the unique
    identifier for this Region, otherwise generates a random identifier UUID.
    Generates factors (list of Intervals) from the lower and upper vertices.
    If this region is a result of intersections, the original regions are 
    linked in the property originals; otherwise originals references itself.
    If lower vertex has values greater than its corresponding upper values,
    swaps the lower and upper values. Additional named arguments given will
    be assigned as data properties.

    Args:
      lower, upper:
        The lower and upper bounding vertices.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
      originals:
        List of the original intersecting regions that
        formed this region. References itself if this
        region is an original one.
      kwargs:
        To be assigned as data properties.
    """
    if len(id) == 0:
      id = str(uuid4())
    
    if len(originals) == 0:
      originals = [id]

    assert len(id) > 0
    assert isinstance(lower, List) and all([isinstance(l, Real) for l in lower])
    assert isinstance(upper, List) and all([isinstance(u, Real) for u in upper])
    assert isinstance(originals, List) and all(isinstance(x, str) for x in originals)
    assert len(lower) > 0 and len(lower) == len(upper)
    assert all(isinstance(x, str) for x in kwargs.keys())

    self.id = id
    self.dimension = len(lower)
    self.factors = [Interval(*i) for i in zip(lower, upper)]
    self.originals = originals
    self.data = {}
    for k, v in kwargs.items():
      self.data[k] = v


  ### Properties: Getters

  @property
  def lower(self) -> List[float]:
    """
    The lower bounding vertex of this Region. Calculate and return a copy of
    the vector that represents the lower bounding values for this Region in
    each dimension.

    Returns:
      The lower bounding vertex of this Region.
    """
    return [d.lower for d in self.factors]

  @property
  def upper(self) -> List[float]:
    """
    The upper bounding vertex of this Region. Calculate and return a copy of
    the vector that represents the upper bounding values for this Region in
    each dimension.

    Returns:
      The upper bounding vertex of this Region.
    """
    return [d.upper for d in self.factors]

  @property
  def lengths(self) -> List[float]:
    """
    The distances between the lower and upper bounding
    vertices on each dimension.

    Returns:
      List of distances for each dimension.
    """
    return [d.length for d in self.factors]

  @property
  def midpoint(self) -> List[float]:
    """
    The point equal distance between the lower and
    upper bounding vertices.

    Returns:
      The point at the midpoint or center of
      Region along all dimensions.
    """
    return [d.midpoint for d in self.factors]

  @property
  def size(self) -> float:
    """
    The magnitude size of the Region; length, area, volume.
    Computed by multiply all the dimensional lengths (sides) together.

    Returns:
      The magnitude size of the Region.
    """
    return reduce(lambda x, y: x * y, self.lengths)


  ### Methods: Syntactic sugar

  def __hash__(self) -> str:
    """
    Return the hash value for this object.
    Two objects that compare equal must also have the same hash value,
    but the reverse is not necessarily true.

    Returns:
      The hash value for this object.
    """
    return hash(self.id)


  def __getitem__(self, index: Union[int, str]) -> Union[Interval, Any]:
    """
    Retrieves the Interval for associated dimension when index is an int.
    Retrieves the data value for associated data property when index is a str.

    Is syntactic sugar for:
      interval  = self[dimension]
      datavalue = self[datakey]

    Overload Method that wraps:
      self.factors[index]
      self.data[index]

    Args:
      index:
        Lookup key for:
        - Index of dimension when int or
        - Data key in data properties when str.

    Returns:
      Interval for associated dimension:  index is int.
      Data value in data property:        index is str.

    Raises:
      IndexError: dimension out of range, when index is int.
      KeyError:   datakey does not exist, when index is str.
    """
    if isinstance(index, int):
      return self.factors[index]
    else:
      return self.data[index]


  def __setitem__(self, index: Union[int, str], value: Union[Interval, Any]):
    """
    Assigns the given index as int (dimension) with the given Interval.
    Assigns the given index as str (datakey) with the given value to the
    data properties.

    Is syntactic sugar for:
      self[dimension] = interval
      self[datakey] = datavalue

    Args:
      index:
        Lookup key for:
        - Index of dimension when int or
        - Data key in data properties when str.
      value:
        Interval for associated dimension when index is int.
        Data value in data property when index is str.
    """
    if isinstance(index, str):
      self.data[index] = value
    else:
      assert isinstance(index, int)
      assert isinstance(value, Interval)
      assert 0 <= index < self.dimension

      self.factors[index] = value


  ### Methods: Representations

  def __repr__(self) -> str:
    """
    Called by the repr() built-in function to compute the “official” string
    representation of an object. If at all possible, this should look like a
    valid Python expression that could be used to recreate an object with the
    same value (given an appropriate environment).

    Returns:
      String representation of an object.
    """
    dictobj = {
      'id': self.id[0:8] if len(self.id) > 8 else self.id,
      'lower': self.lower,
      'upper': self.upper,
      'originals': [o[0:8] if len(o) > 8 else o for o in self.originals]
    }

    dicttopairs = lambda item: f'{item[0]}={item[1]}'
    dictkvpairs = ', '.join(map(dicttopairs, dictobj.items()))

    return f'{self.__class__.__name__}({dictkvpairs})'


  ### Methods: Clone

  def __copy__(self) -> 'Region':
    """
    Create a shallow copy of this Region and return it. The lower and upper
    values will remain the same. The 'id' is different. The data property
    object is copied, but the object items are references to original values.

    Returns:
      The newly created Region copy.
    """
    return Region(self.lower, self.upper, **self.data)


  def copy(self) -> 'Region':
    """
    Alias for self.__copy__(self)
    """
    return self.__copy__()


  def __deepcopy__(self, memo: Dict = {}) -> 'Region':
    """
    Create a deep copy of this Region and return it. The lower and upper
    values will remain the same. The 'id' is different. The data property
    object is copied with each item recursively copied.

    Args:
      memo: The dictionary of objects already copied
            during the current copying pass.

    Returns:
      The newly created Region copy.
    """
    mkey, data = id(self), self.data.copy()

    if mkey in memo:
      return memo[mkey]

    for k, v in data.items():
      if callable(getattr(v, '__deepcopy__')):
        data[k] = memo.setdefault(id(v), v.__deepcopy__(memo))
      elif callable(getattr(v, '__copy__')):
        data[k] = memo.setdefault(id(v), v.__copy__())
      else:
        data[k] = memo.setdefault(id(v), v)

    region = Region(self.lower, self.upper, **data)
    memo[mkey] = region
    return region


  def deepcopy(self, memo: Dict = {}) -> 'Region':
    """
    Alias for self.__deepcopy__(memo)
    """
    return self.__deepcopy__(memo)

  ### Methods: Data Assignment


  def getdata(self, key: str, default: Any = None) -> Any:
    """
    Return the data value for key if key is in this Region's data
    dictionary, else 'default'. If 'default' is not given, it defaults to None,
    so that this method never raises a KeyError.

    Args:
      key, default:
        Arguments for self.data.get().

    Returns:
      This Region's data value or the default.
    """
    return self.data.get(key, default)


  def initdata(self, key: str, default: Any = None) -> Any:
    """
    If key is in this Region's data dictionary, return its value.
    If not, insert key with a value of 'default' and return 'default'.
    'default' defaults to None.

    Args:
      key, default:
        Arguments for self.data.setdefault().

    Returns:
      This Region's data value or the default.
    """
    return self.data.setdefault(key, default)


  def removedata(self, key: str, default: Any = None) -> Any:
    """
    If key is in this Region's data dictionary, remove it and return its
    value, else return 'default'. If 'default' is not given and key is not
    in the data dictionary, a KeyError is raised.

    Args:
      key, default:
        Arguments for self.data.pop().

    Returns:
      This Region's removed data value or the default.

    Raises:
      KeyError: If 'default' is not given and
                key is not in the data dictionary.
    """
    return self.data.pop(key, default)


  ### Methods: Intersection and other spatial queries

  def contains(self, point: List[float], inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the point lies within the lower and upper bounding vertices.

    Args:
      point:
        The point to test if it lies within
        this Region's bounds.
      inc_lower, inc_upper:
        Boolean flag for whether or not to include or
        to exclude the lower or upper bounding vertics
        of this Region. If inc_lower is True, includes
        the lower bounding vertex, otherwise excludes it.
        Likewise, if inc_upper is True, includes the
        upper bounding vertex, otherwise excludes it.

    Returns:
      True:   If point lies within the Region.
      False:  Otherwise.
    """
    assert isinstance(point, List)
    assert all([isinstance(x, float) for x in point])
    assert self.dimension == len(point)

    return all([d.contains(point[i], inc_lower, inc_upper) \
                for i, d in enumerate(self.factors)])


  def encloses(self, that: 'Region', inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if that Region lies within this Region.

    Args:
      that:
        The other Region to test if it lies entirely
        within this Region's bounds.
      inc_lower, inc_upper:
        Boolean flag for whether or not to include or
        to exclude the lower or upper bounding vertics
        of this Region. If inc_lower is True, includes
        the lower bounding vertex, otherwise excludes it.
        Likewise, if inc_upper is True, includes the
        upper bounding vertex, otherwise excludes it.

    Returns:
      True:   If that Region lies entirely within
              this Region.
      False:  Otherwise.
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if self == that:
      return True

    return all([d.encloses(that[i], inc_lower, inc_upper) \
                for i, d in enumerate(self.factors)])


  def __contains__(self, value: Union['Region', List[float], str]) -> bool:
    """
    Determine if the point or Region (value) lies entirely between this
    Region's lower and upper bounding vertices, inclusively. Return True
    if point or Region is entirely within this Region, otherwise False.

    Determine if this Region has the given data property, if given
    value is a str. Return True if value is in data properties,
    otherwise False.

    Is syntactic sugar for:
      value in self

    Overload Method that wraps:
      self.contains when value is a point,
      self.encloses when value is a Region, and
      self.data.__contains__ when value is a str

    Args:
      value:
        The point to test if it lies within this Region's
        bounds, the other Region to test if it lies
        entirely within this Region's bounds, or the data
        property exists within this Region.

    Returns:
      True:   If the point or other Region lies entirely
              within this Region's bounds, or if the data
              property exists within this Region.
      False:  Otherwise.
    """
    if isinstance(value, Region):
      return self.encloses(value)
    elif isinstance(value, str):
      return value in self.data
    else:
      return self.contains(value)


  def is_intersecting(self, that: 'Region', inc_bounds = False) -> bool:
    """
    Determine if the given Region intersects with this Region.
    If the regions are exactly adjacent (one's lower is equal other's upper),
    then if they intersect or not is decided by inc_bounds flag.
    To be intersecting, one Region must contain the other's lower or
    upper bounding vertices. As long as all corresponding Intervals for each
    dimension intersect in both Region, then the Regions are intersecting.
    Return True if given Region intersects with this Region, otherwise False.

    Args:
      that:
        The other Region to test if it intersects
        with this Region.
      inc_bounds:
        If regions considered intersecting when
        lower/upper bounds are exactly equal
        (zero-length intersection)

    Returns:
      True:   If other Region intersects with this Region
      False:  Otherwise.

    Examples:

      Intersecting:
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

      Not Intersecting:

      - |--------------| 
        |<- Region A ->| |--------------|
        |--------------| |<- Region B ->|
                         |--------------|

      Conditionally Intersecting:
      - |--------------|
        |<- Region A ->|
        |==============|
        |<- Region B ->|
        |--------------|

    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    return all([d.is_intersecting(that[i]) for i, d in enumerate(self.factors)])


  def __eq__(self, that: 'Region') -> bool:
    """
    Determine if the given Region equals to this Region.
    If the two Region have the same factors (same Intervals; lower and
    upper bounds for all dimensions), then they are equal, otherwise they
    are not. Return True if the two Regions are equal, otherwise False.

    Is syntactic sugar for:
      self == that

    Args:
      that:
        The other Region to test if it has the
        same Intervals (lower and upper bounds) for
        all dimensions within this Region's bounds.

    Returns:
      True:   If the two Regions are equal.
      False:  Otherwise.
    """
    return isinstance(that, Region) and \
           self.dimension == that.dimension and \
           all([d == that[i] for i, d in enumerate(self.factors)])


  def get_intersection(self, that: 'Region', inc_bounds = False) -> 'Region':
    """
    Compute the intersecting Region between this and that Region.

    Args:
      that:
        The other Region with which to compute
        the common intersecting Region.
      inc_bounds:
        If regions considered intersecting when
        lower/upper bounds are exactly equal
        (results in zero-length intersection)

    Returns:
      The intersecting Region
      None: If the Regions do not intersect.

    Examples:

    - |---Region A---|          -        |---Region B---|
      |     |---Region B---|      |---Region A---|      |
      |     |########|     |      |      |#######|      |
      |     |########|     |      |      |#######|      |
      |-----|--------|     |      |      |-------|------|
            |--------------|      |--------------|

    - |------Region A------|    - |------Region A------|
      |  |---Region B---|  |      |  |---Region B---|  |
      |  |##############|  |      |  |##############|  |
      |  |##############|  |      |  |##############|  |
      |--|--------------|--|      |  |--------------|  |
         |--------------|         |--------------------|

    -       |---Region B---|    - |===Region A===|
      |---Region A---|     |      |##############|
      |     |########|     |      |##############|
      |     |########|     |      |##############|
      |-----|--------|     |      |##############|
            |--------------|      |===Region B===|
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if not self.is_intersecting(that, inc_bounds):
      return None

    return Region.from_intersection([self, that])


  ### Methods: Size queries

  def get_intersection_size(self, that: 'Region') -> float:
    """
    Compute the size of the intersection between this and that Region.
    There's no need to check for exact bounds, as the size would be 0 anyway.

      Args:
        that:
          The other Region with which to compute
          the common intersecting Region.

      Returns:
        The size of the intersection
        0: If the Regions do not intersect.
      """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if not self.is_intersecting(that):
      return 0

    return self.get_intersection(that).size


  def get_union_size(self, that: 'Region') -> float:
    """
    Compute the size of the union of two Regions.

    Args:
      that:
        The other Region which this Region is to compute
        the enclosing (union) Region with.

    Returns:
      The size of the union.

    Examples:

    - |## Region A ##|^^^^^|    - |^^^^^|## Region B ##|
      |#####|%% Region B %%|      |%% Region A %%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      |.....|%%%%%%%%%%%%%%|      |%%%%%%%%%%%%%%|.....|

    - |%%%%% Region A %%%%%|    - |%%%%% Region A %%%%%|
      |%%|## Region B ##|%%|      |%%|## Region B %%|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |..|##############|..|      |%%%%%%%%%%%%%%%%%%%%|

    - |^^^^^^|%% Region B %%|   - |## Region A ##|
      |## Region A ##|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |......|%%%%%%%%%%%%%%|     |## Region B ##|
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if not self.is_intersecting(that):
      return self.size + that.size

    return self.size + that.size - get_intersection_size(that)


  def project(self, dimension: int,
                    interval: Interval = Interval(0, 0),
                    **kwargs) -> 'Region':
    """
    Project this Region to the specified number of dimensions.
    If the given number of dimensions is greater than this Region's
    dimensionality, output a Region with additional factors with the given
    Interval or [0, 0]  intervals. If the given number of dimensions is less
    than this Region's dimensionality, output a Region with the additional
    dimensions removed. If the given dimension number is equal to this
    Region's dimensionality, outputs a copy of this Region. Additional
    arguments passed through to Region.from_intervals.

    Args:
      dimension:
        The number of dimensions in the output
        projected Region.
      interval:
        The Interval to add to each dimension if
        the projected number of dimension is greater
        than this Region.
      kwargs:
        Additional arguments passed through to
        Region.from_intervals.

    Returns:
      The projected Region.
    """
    assert dimension > 0

    factors = [Interval(interval.lower, interval.upper)
                  if d >= self.dimension else self[d] 
                  for d in range(dimension)]

    return Region.from_intervals(factors, **kwargs)


  ### Class Methods: Generators

  @classmethod
  def from_intervals(cls, factors: List[Interval], originals: List['Region'] = [],
                          id: str = '', **kwargs) -> 'Region':
    """
    Construct a new Region from the given a list of Intervals.

    Args:
      factors:
        List of Intervals for each dimension
        within the Region. A Region of N dimensions
        is created from a list of N Intervals.
      originals:
        List of the original intersecting regions that
        formed this region. References itself if this
        region is an original one.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
      kwargs:
        Additional arguments passed through to
        Region.__init__.

    Returns:
      A Region of dimension N, for a list of
      Intervals of length N.
    """
    assert isinstance(factors, List)
    assert all([isinstance(d, Interval) for d in factors])
    assert isinstance(originals, List) and all(isinstance(x, str) for x in originals)
    
    return cls([d.lower for d in factors],
               [d.upper for d in factors], originals, id, **kwargs)


  @classmethod
  def from_interval(cls, interval: Interval,
                         dimension: int = 1,
                         originals: List['Region'] = [],
                         id: str = '', **kwargs) -> 'Region':
    """
    Construct a new Region from a given Interval and the specified number of
    dimensions. Returns a Region contains the specified dimensionality with
    each dimension having the same Interval.

    Args:
      interval:
        The Interval to be projected for each
        dimension in the new Region.
      dimension:
        The number of dimensions in the new
        projected Region.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
      kwargs:
        Additional arguments passed through to
        Region.__init__.

    Returns:
      A Region containing the specified dimensionality
      with each dimension having the same Interval.
    """
    assert isinstance(interval, Interval)
    assert isinstance(dimension, int) and dimension > 0

    return cls([interval.lower] * dimension,
               [interval.upper] * dimension, id, **kwargs)


  @classmethod
  def from_intersection(cls, regions: List['Region'],
                         id: str = '') -> Union['Region', None]:
    """
    Constructs a new Region from the intersection of two or more given Regions.

    Args:
      regions:
        The list of Regions which the intersecting
        Region is generated with.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.

    Returns:
      The intersecting Region.
      None: If the Regions do not intersect.
    """
    assert isinstance(regions, List) and len(regions) > 1
    assert all([isinstance(r, Region) for r in regions])
    assert all([regions[0].dimension == r.dimension for r in regions])

    factors = zip(*list(map(lambda r: r.factors, regions)))
    factors = [Interval.from_intersection(list(f)) for f in factors]

    if any([f == None for f in factors]):
      return None

    originals = list({o for r in regions for o in r.originals})

    return cls.from_intervals(factors, originals, id)


  ### Methods: (De)serialization

  def to_dict(self) -> Dict:
    """
    Generates a dict object from this Region object that can be serialized.

    Returns:
      The generated dict.
    """

    return asdict(self)


  @classmethod
  def from_dict(cls, object: Dict, id: str = '') -> 'Region':
    """
    Construct a new Region from the conversion of the given Dict.
    The Dict must contain one of the following combinations of fields:

    - lower (List[float]) and upper (List[float])
    - factors (List[Interval-equivalent])
    - dimension (int) and interval (Interval-equivalent)
    - dimension (int), lower (float or List[float]) and
      upper (float or List[float])

    Note:
    - Interval-equivalent means parseable by
      Interval.from_dict.

    Args:
      object:
        The Dict to be converted to a Region
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.

    Returns:
      The newly constructed Region.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
    """
    assert isinstance(object, Dict)
    id, data = object.get('id', id), object.get('data', {})
    assert isinstance(data, Dict)

    if 'originals' not in object:
      object['originals'] = [id]

    if 'lower' in object and 'upper' in object:
      assert isinstance(object['lower'], List) and all([isinstance(x, Real) for x in object['lower']])
      assert isinstance(object['upper'], List) and all([isinstance(x, Real) for x in object['upper']])
      assert len(object['lower']) == len(object['upper'])
      return cls(object['lower'], object['upper'], object['originals'], id, **data)

    elif 'factors' in object:
      assert isinstance(object['factors'], List)
      return cls.from_intervals([Interval.from_dict(f) for f in object['factors']],
        object['originals'], id, **data)
    else:
      raise ValueError('Unrecognized Region representation')


  @classmethod
  def from_object(cls, object: Any, id: str = '') -> 'Region':
    """
    Construct a new Region from the conversion of the given object.
    The object must contain one of the following representations:

    - A Dict that is parseable by the from_dict method.
    - A List of objects that are parseable by
      Interval.from_dict, to be passed to the
      from_intervals method.
    - A Tuple containing 2 values:
      - An int as the number of dimension,
        to be passed to from_interval and
      - An object that is parseable by the
        Interval.from_dict method.

    Args:
      object:
        The object to be converted to a Region
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.

    Returns:
      The newly constructed Region.

    Raises:
      ValueError:
        If object does not have one of the above
        combinations of fields.
    """
    if isinstance(object, Dict):
      return cls.from_dict(object, id)
    elif isinstance(object, List):
      return cls.from_intervals(list(map(Interval.from_dict, object)), [], id)
    elif isinstance(object, Tuple):
      assert len(object) == 2
      assert isinstance(object[0], int) and 0 < object[0]
      return cls.from_interval(Interval.from_dict(object[1]), object[0], [], id)
    else:
      raise ValueError('Unrecognized Region representation')
