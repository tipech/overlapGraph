#!/usr/bin/env python

#
# datastructs/region.py - Region class
#
# This script implements the Region class, a data class that defines a
# multidimensional region, with an upper and a lower vertex. Each region
# has a defined dimensionality. Provides methods for determining if there
# is an overlap between two regions, what the intersection or union regions
# between the two regions are, and randomly generate regions and points
# within a region.
#

from dataclasses import asdict, astuple, dataclass, field
from functools import reduce
from numbers import Real
from typing import Any, Callable, Dict, List, Tuple, Union
from uuid import uuid4

from ..helpers.randoms import NDArray, RandomFn, Randoms
from .interval import Interval
from .ioable import IOable


RegionPair = Tuple['Region', 'Region']

@dataclass
class Region(IOable):
  """
  Dataclass that defines a multidimensional region, with an upper and a
  lower vertex. Each region has a defined dimensionality. Provides methods
  for determining if there is an overlap between two regions, what the
  intersection and union regions between the two regions are, and
  randomly generate regions and points within a region.

  Properties:           id, lower, upper, dimension, dimensions, data
  Computed Properties:  lengths, midpoint, size
  Special Methods:      __init__, __getitem__, __setitem__, __repr__, __contains__, __eq__
  Methods:              contains, encloses, overlaps, intersect, union,
                        project, random_points, random_regions
  Class Methods:        from_intervals, from_interval,
                        from_intersect, from_union, from_dict

  Inherited from IOable:
    Methods:            to_output
    Class Methods:      from_text, from_source
      Overridden:       to_object, from_object
  """
  id: str
  lower: List[float]
  upper: List[float]
  dimension: int = field(repr=False)
  dimensions: List[Interval] = field(repr=False)
  data: Dict = field(repr=False)

  def __init__(self, lower: List[float], upper: List[float], id: str = '', dimension: int = 0, **kwargs):
    """
    Initialize a new Region, with the lower and upper bounding vertices.
    If dimension is specified, the lower and upper vertices must match that number of
    dimensions (dimensionality), otherwise computes the dimension from the lower and
    upper vertices, which must have matching number of dimensions.
    If id is specified, sets it as the unique identifier for this Region,
    otherwise generates a random identifier, UUID v4.
    Additional named arguments given will be assigned to as data properties.
    Generates the dimensions (list of Intervals) from the lower and upper vertices.
    If lower vertex has values greater than its corresponding upper values,
    swaps the lower and upper values.

    :param lower:
    :param upper:
    :param id:
    :param dimension:
    :param kwargs:
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
    self.data = {}
    for k, v in kwargs.items():
      self.data[k] = v

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

  def __getitem__(self, index: Union[int, str]) -> Union[Interval, Any]:
    """
    For Type index: int
      Given a dimension (index) as int, returns the Interval for that dimension.
      Syntactic sugar: self[dimension] -> Interval
    
    For Type index: str
      Given a datakey (index) as string, returns the datavalue for that datakey.
      Syntactic sugar: self[datakey] -> datavalue

    :param index:
    """
    if isinstance(index, int):
      return self.dimensions[index]
    elif index in self.data:
      return self.data[index]

  def __setitem__(self, index: Union[int, str], value: Union[Interval, Any]):
    """
    For Type index: int
      Given a dimension (index) as int and the Interval for that dimension, updates
      the dimensions as well as the lower and upper values.
      Syntactic sugar: self[dimension] = Interval

    For Type index: str
      Given a datakey (index) as string and the datavalue for that datakey,
      assigns or updates the data key with the given data value.
      Syntactic sugar: self[datakey] = datavalue

    :param index:
    :param value:
    """
    if isinstance(index, str):
      self.data[index] = value
    else:
      assert isinstance(index, int)
      assert isinstance(value, Interval)
      assert 0 <= index < self.dimension

      self.dimensions[index] = value
      self.lower[index] = value.lower
      self.upper[index] = value.upper

  def __repr__(self) -> str:
    """
    Called by the repr() built-in function to compute the “official” string
    representation of an object. If at all possible, this should look like a
    valid Python expression that could be used to recreate an object with the
    same value (given an appropriate environment).
    """
    dictobj = {
      'id': self.id[0:8] if len(self.id) > 8 else self.id,
      'lower': self.lower,
      'upper': self.upper
    }

    dicttopairs = lambda item: f'{item[0]}={item[1]}'
    dictkvpairs = ', '.join(map(dicttopairs, dictobj.items()))

    return f'{self.__class__.__name__}({dictkvpairs})'

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
    assert isinstance(point, List)
    assert all([isinstance(x, float) for x in point])
    assert self.dimension == len(point)

    return all([d.contains(point[i], inc_lower, inc_upper) for i, d in enumerate(self.dimensions)])

  def encloses(self, that: 'Region', inc_lower = True, inc_upper = True) -> bool:
    """
    Determine if the region lies within the lower and upper bounding vertices - this Region.
    If inc_lower is True, includes the lower vertex, otherwise excludes lower vertex.
    If inc_upper is True, includes the upper vertex, otherwise excludes upper vertex.
    Return True if region lies within the lower and upper bounding vertices, otherwise False.

    :param that:
    :param inc_lower:
    :param inc_upper:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if self == that:
      return True

    return all([d.encloses(that[i], inc_lower, inc_upper) for i, d in enumerate(self.dimensions)])

  def __contains__(self, value: Union['Region', List[float]]) -> bool:
    """
    For Type value: List[float]
      Determine if the point lies within the lower and upper bounding vertices (inclusively).
      Return True if point lies within the lower and upper bounding vertices, otherwise False.
      Same as: self.contains(point, inc_lower = True, inc_upper = True)
      Syntactic Sugar: point in self

    For Type value: Region
      Determine if the region lies within the lower and upper bounding vertices (inclusively).
      Return True if region lies within the lower and upper bounding vertices, otherwise False.
      Same as: self.encloses(that, inc_lower = True, inc_upper = True)
      Syntactic Sugar: that in self

    :param value:
    """
    if isinstance(value, Region):
      return self.encloses(value)
    else:
      return self.contains(value)

  def __eq__(self, that: 'Region') -> bool:
    """
    Determine if the given Region equals to this Region.
    If the two Region have the same dimensions, then they are equal,
    otherwise they do not equal. Return True if the two Regions are
    equal, otherwise False. Syntactic Sugar: self == that

    :param that:
    """
    return that is not None and \
           all([isinstance(that, Region), self.dimension == that.dimension]) and \
           all([d == that[i] for i, d in enumerate(self.dimensions)])

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

  def intersect(self, that: 'Region', linked: Union[bool, str] = False) -> 'Region':
    """
    Compute the overlapping Region between this Region and the given Region.
    If linked is given, adds a data property 'intersect' that either:
    
    - 'reference': Holds the reference to this Region and its intersecting (that) Region, or
    - 'aggregate': Holds all references to the intersecting Regions, including previous intersections.

    Return the overlapping Region or None if the Regions do not overlap.

    - |---Region A---|          -        |---Region B---|
      |     |---Region B---|      |---Region A---|      |
      |     |#######|      |      |      |#######|      |
      |     |#######|      |      |      |#######|      |
      |-----|-------|      |      |      |-------|------|
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

    :param that:
    :param linked:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    if not self.overlaps(that):
      return None

    data = {}
    if any([linked == True, linked == 'reference', \
            linked == 'aggregate' and 'intersect' not in self.data]):
      data['intersect'] = [self, that]
    elif 'intersect' in self.data:
      assert isinstance(self['intersect'], List)
      data['intersect'] = self['intersect'].copy()
      data['intersect'].append(that)
    elif linked != False:
      raise ValueError(f'Invalid linked "{linked}" mode')

    return Region.from_intervals([d.intersect(that[i]) for i, d in enumerate(self.dimensions)], **data)

  def union(self, that: 'Region', linked: Union[bool, str] = False) -> 'Region':
    """
    Compute the Region that encloses both this Region and the given Region.
    If linked is given, adds a data property 'union' that either:
    
    - 'reference': Holds the reference to this Region and its uniting (that) Region, or
    - 'aggregate': Holds all references to the enclosing Regions, including previous unions.

    Return the enclosing Region.

    - |## Region A ##|`````;    - |`````|:::Region B:::|
      |#####|%% Region B %%|      |%% Region A %%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      |#####|########|%%%%%|      |%%%%%|%%%%%%%%|#####|
      '.....|%%%%%%%%%%%%%%|      |%%%%%%%%%%%%%%|.....|

    - |%%%%% Region A %%%%%|    - |%%%%% Region A %%%%%|
      |%%|## Region B ##|%%|      |%%|## Region B %%|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |%%|##############|%%|      |%%|##############|%%|
      |..|##############|..|      |%%%%%%%%%%%%%%%%%%%%|

    - |``````|%% Region B %%|   - |## Region A ##|
      |## Region A ##|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |######|#######|%%%%%%|     |##############|
      |......|%%%%%%%%%%%%%%|     |## Region B ##|

    :param that:
    :param linked:
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    data = {}
    if any([linked == True, linked == 'reference', \
            linked == 'aggregate' and 'union' not in self.data]):
      data['union'] = [self, that]
    elif linked == 'aggregate':
      assert isinstance(self['union'], List)
      data['union'] = self['union'].copy()
      data['union'].append(that)
    elif linked != False:
      raise ValueError(f'Invalid linked "{linked}" mode')

    return Region.from_intervals([d.union(that[i]) for i, d in enumerate(self.dimensions)], **data)

  def project(self, dimension: int, **kwargs) -> 'Region':
    """
    Project this Region to the specified number of dimensions. If the given
    number of dimensions is greater than this Region's dimensionality, output
    a Region with additional dimensions with [0, 0] intervals. If the given
    number of dimensions is less than this Region's dimensionality, output a
    Region with the additional dimensions removed. If the given number of
    dimensions is less than this Region's dimensionality, outputs a copy of
    this Region. Additional arguments passed through to Region.from_intervals.

    :param dimension:
    :param kwargs:
    """
    assert dimension > 0

    if dimension == self.dimension:
      return Region.from_intervals(self.dimensions, **kwargs)
    else:
      return Region.from_intervals([(Interval(0, 0) if d >= self.dimension \
                                                    else self[d]) for d in range(dimension)], **kwargs)

  def random_points(self, npoints: int = 1, randomng: RandomFn = Randoms.uniform()) -> NDArray:
    """
    Randomly draw N samples from a given distribution or random
    number generation function. Samples are drawn over the interval
    [lower, upper) specified by this Region. The given size N specifies
    the number of points to output. The default npoints is 1; a single point
    is returned. Otherwise, a list with the specified number of samples
    are drawn. Each point will have the same dimensionality as this Region.

    The default behavior is that samples are uniformly distributed.
    In other words, any point within the given Region is equally
    likely to be drawn by uniform. Other distribution or random
    number generation functions can be substituted via the `randomng`
    parameter.

    :param npoints:
    :param randomng:
    """
    assert isinstance(npoints, int) and npoints > 0
    assert isinstance(randomng, Callable)

    return randomng([npoints, self.dimension], self.lower, self.upper)

  def random_regions(self, nregions: int = 1, sizepc_range: 'Region' = None,
                           posnrng: RandomFn = Randoms.uniform(),
                           sizerng: RandomFn = Randoms.uniform(),
                           precision: int = None,
                           **kwargs) -> List['Region']:
    """
    Randomly generate N Regions within this Regions, each with a random size
    as a percentage of the total Region dimensions, bounded by the given size
    percentage Region (enclosed by Region([0, ...], [1, ...])). All subregions
    must have the same number of dimensions as this Region. The default
    distributions for choosing the position of the Region and its size percentage
    are uniform distributions, but can be substituted for other distribution or
    random number generation functions via the `posnrng` and `sizerng` parameter.
    If precision is given, return the randomly generated Intervals where the lower
    and upper bounding values are rounded/truncated to the specified precision
    (number of digits after the decimal point). If precision is None, the lower
    and upper bounding values are of arbitrary precision. Additional arguments
    passed through to Region.from_intervals.

    :param nregions:
    :param sizepc_range:
    :param posnrng:
    :param sizerng:
    :param precision:
    :param kwargs:
    """
    ndunit_region = Region([0] * self.dimension, [1] * self.dimension)
    if sizepc_range == None:
      sizepc_range = ndunit_region

    assert isinstance(sizepc_range, Region) and self.dimension == sizepc_range.dimension
    assert ndunit_region.encloses(sizepc_range)
    assert isinstance(posnrng, Callable) and isinstance(sizerng, Callable)

    regions = []
    for _ in range(nregions):
      region = []
      for i, d in enumerate(self.dimensions):
        dimension = d.random_intervals(1, sizepc_range[i], posnrng, sizerng, precision)[0]
        region.append(dimension)
      regions.append(Region.from_intervals(region, **kwargs))
    return regions

  @classmethod
  def from_intervals(cls, dimensions: List[Interval], id: str = '', **kwargs) -> 'Region':
    """
    Construct a new Region from the given a list of Intervals.
    If id is specified, sets it as the unique identifier for this Region,
    otherwise generates a random identifier, UUID v4.
    Additional arguments passed through to Region.__init__.
    Returns a Region of dimension X, for a list of Intervals of length X.

    :param dimensions:
    :param id:
    :param kwargs:
    """
    assert isinstance(dimensions, List)
    assert all([isinstance(d, Interval) for d in dimensions])

    return cls([d.lower for d in dimensions],
               [d.upper for d in dimensions], id, **kwargs)

  @classmethod
  def from_interval(cls, interval: Interval, dimension: int = 1, id: str = '', **kwargs) -> 'Region':
    """
    Construct a new Region from a given Intervals and the specified
    number of dimensions. Returns a Region contains the specified
    dimensionality with each dimension have the same Interval.
    If id is specified, sets it as the unique identifier for this Region,
    otherwise generates a random identifier, UUID v4.
    Additional arguments passed through to Region.__init__.

    :param interval:
    :param dimension:
    :param id:
    :param kwargs:
    """
    assert isinstance(interval, Interval)
    assert isinstance(dimension, int) and dimension > 0

    return cls([interval.lower] * dimension,
               [interval.upper] * dimension, id, **kwargs)

  @classmethod
  def from_intersect(cls, regions: List['Region'], linked: bool = False, id: str = '') -> Union['Region', None]:
    """
    Constructs a new Region from the intersection of the given Regions.
    If linked is True, adds a data property 'intersect' that holds the
    references to its given intersecting Regions. If id is specified,
    sets it as the unique identifier for this Region, otherwise generates
    a random identifier, UUID v4. Return the overlapping Region or None
    if the Regions do not all overlap.

    :param regions:
    :param linked:
    :param id:
    """
    assert isinstance(regions, List) and len(regions) > 1
    assert all([isinstance(r, Region) for r in regions])
    assert all([regions[0].dimension == r.dimension for r in regions])
    
    dimensions = zip(*list(map(lambda r: r.dimensions, regions)))
    dimensions = [Interval.from_intersect(list(d)) for d in dimensions]
    if any([d == None for d in dimensions]):
      return None

    data = {'intersect': regions.copy()} if linked else {}

    return cls.from_intervals(dimensions, id, **data)

  @classmethod
  def from_union(cls, regions: List['Region'], linked: bool = False, id: str = '') -> 'Region':
    """
    Constructs a new Region from the union of the given Regions.
    If linked is True, adds a data property 'union' that holds the
    references to its given uniting Regions. If id is specified,
    sets it as the unique identifier for this Region, otherwise generates
    a random identifier, UUID v4. Return the enclosing Region.

    :param regions:
    :param linked:
    :param id:
    """
    assert isinstance(regions, List) and len(regions) > 1
    assert all([isinstance(r, Region) for r in regions])
    assert all([regions[0].dimension == r.dimension for r in regions])

    dimensions = zip(*list(map(lambda r: r.dimensions, regions)))
    dimensions = [Interval.from_union(list(d)) for d in dimensions]
    data = {'union': regions.copy()} if linked else {}

    return cls.from_intervals(dimensions, id, **data)

  @classmethod
  def to_object(cls, object: 'Region', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given Region object that
    can be converted or serialized as the specified data format: 'json'. Additional
    arguments passed via kwargs are used to the customize and tweak the object
    generation process.

    :param object:
    :param format:
    :param kwargs:
    """
    assert isinstance(object, Region)

    fieldnames = ['id', 'dimension', 'dimensions', 'data']

    if 'compact' in kwargs and kwargs['compact']:
      dictobj = dict(map(lambda f: (f, getattr(object, f)), fieldnames))

      if 'data' in dictobj:
        if dictobj['data'] is object.data:
          dictobj['data'] = dictobj['data'].copy()
        if 'intersect' in dictobj['data']:
          dictobj['data']['intersect'] = map(lambda r: r.id, dictobj['data']['intersect'])
        if 'union' in dictobj['data']:
          dictobj['data']['union'] = map(lambda r: r.id, dictobj['data']['union'])
        if len(dictobj['data']) == 0:
          del dictobj['data']

      return dictobj
    else:
      return asdict(object)

  @classmethod
  def from_dict(cls, object: Dict, id: str = '') -> 'Region':
    """
    Construct a new Region from the conversion of the given Dict.
    The Dict must contains one of the following combinations of fields:

    - lower (List[float]) and upper (List[float])
    - dimensions (List[Interval-equivalent])
    - dimension (int) and interval (Interval-equivalent)
    - dimension (int), lower (float or List[float]) and upper (float or List[float])

    Interval-equivalent means parseable by Interval.from_object.
    If id is specified, sets it as the unique identifier for this Region, otherwise
    generates a random identifier, UUID v4. If object does not have one of the above 
    combinations of fields, raises ValueError. Returns the newly constructed Region.

    :param object:
    :param id:
    """
    assert isinstance(object, Dict)

    if 'id' in object:
      id = object['id']
    
    data = {}
    if 'data' in object:
      assert isinstance(object['data'], Dict)
      data = object['data']

    if 'dimension' in object and any([k in object for k in ['lower', 'upper']]):
      assert isinstance(object['dimension'], int) and 0 < object['dimension']
      for k in ['lower', 'upper']:
        if isinstance(object[k], Real):
          object[k] = [object[k]] * object['dimension']

    if all([k in object for k in ['lower', 'upper']]):
      assert isinstance(object['lower'], List) and all([isinstance(x, Real) for x in object['lower']])
      assert isinstance(object['upper'], List) and all([isinstance(x, Real) for x in object['upper']])
      assert len(object['lower']) == len(object['upper'])
      return cls(object['lower'], object['upper'], id, **data)
    elif all([k in object for k in ['dimension', 'interval']]):
      assert isinstance(object['dimension'], int) and 0 < object['dimension']
      return cls.from_interval(Interval.from_object(object['interval']), object['dimension'], id, **data)
    elif all([k in object for k in ['dimensions']]):
      assert isinstance(object['dimensions'], List)
      return cls.from_intervals(list(map(Interval.from_object, object['dimensions'])), id, **data)
    else:
      raise ValueError('Unrecognized Region representation')

  @classmethod
  def from_object(cls, object: Any, id: str = '') -> 'Region':
    """
    Construct a new Region from the conversion of the given object.
    The object must contains one of the following representations:

    - A Dict that is parseable by the from_dict method.
    - A List of objects that are parseable by Interval.from_object,
      to be passed to the from_intervals method.
    - A Tuple containing 2 values: (1) an int as the number of dimension,
      to be passed to from_interval and (2) an object that is parseable by
      the Interval.from_object method.

    If id is specified, sets it as the unique identifier for this Region, otherwise
    generates a random identifier, UUID v4. If object does not have one of the above
    combinations of fields, raises ValueError. Returns the newly constructed Region.

    :param object:
    :param id:
    """
    if isinstance(object, Dict):
      return cls.from_dict(object, id)
    elif isinstance(object, List):
      return cls.from_intervals(list(map(Interval.from_object, object)), id)
    elif isinstance(object, Tuple):
      assert len(object) == 2
      assert isinstance(object[0], int) and 0 < object[0]
      return cls.from_interval(Interval.from_object(object[1]), object[0], id)
    else:
      raise ValueError('Unrecognized Region representation')
