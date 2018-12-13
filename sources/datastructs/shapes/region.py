#!/usr/bin/env python

"""
Region Data Class

This script implements the Region class, a data class that defines a
multidimensional region, with an upper and a lower vertex. Each region has a
defined dimensionality. Provides methods for determining if there is an
overlap between two regions, what the intersection or union regions between
the two regions are, and randomly generate regions and points within a region.

Classes:
- Region

Types:
- RegionPair
"""

from dataclasses import asdict, astuple, dataclass, field
from functools import reduce
from numbers import Real
from typing import Any, Callable, Dict, List, Tuple, Union
from uuid import uuid4

from sources.datastructs.datasets.ioable import IOable
from sources.datastructs.shapes.interval import Interval
from sources.helpers.randoms import NDArray, RandomFn, Randoms


RegionPair = Tuple['Region', 'Region']


@dataclass
class Region(IOable):
  """
  Dataclass that defines a multidimensional region, with an upper and a
  lower vertex. Each region has a defined dimensionality. Provides methods
  for determining if there is an overlap between two regions, what the
  intersection and union regions between the two regions are, and
  randomly generate regions and points within a region.

  Attributes:
    id:         The unique identifier for this Region.
    dimension:  The number of dimensions (dimensionality).
    dimensions: The Interval (bounds) for each dimension.
    data:       Additional data properties.

  Properties:
    lower, upper:
      The lower and upper bounding vertices.
    lengths:
      The distances between the lower and upper bounding
      vertices on each dimension.
    midpoint:
      The point equal distance between the lower and
      upper bounding vertices.
    size:
      The magnitude size of the region;
      length, area, volume.

  Methods:
    Special:        __init__, __getitem__, __setitem__,
                    __contains__, __eq__, __repr__
    Instance:       contains, encloses,
                    overlaps, intersect, union,
                    project, random_points, random_regions
    Class Methods:  from_intervals, from_interval,
                    from_intersect, from_union, from_dict

  Inherited from IOable:
    Methods:        to_output
    Class Methods:  from_text, from_source
      Overridden:   to_object, from_object
  """
  id: str
  dimension: int = field(repr=False)
  dimensions: List[Interval] = field(repr=False)
  data: Dict = field(repr=False)

  def __init__(self, lower: List[float], upper: List[float], id: str = '',
                     dimension: int = 0, **kwargs):
    """
    Initialize a new Region, with the lower and upper bounding vertices. If
    dimension is specified, the lower and upper vertices must match that
    number of dimensions (dimensionality), otherwise computes the dimension
    from the lower and upper vertices, which must have matching number of
    dimensions. If id is specified, sets it as the unique identifier for this
    Region, otherwise generates a random identifier, UUID v4. Generates the
    dimensions (list of Intervals) from the lower and upper vertices. If lower
    vertex has values greater than its corresponding upper values, swaps the
    lower and upper values. Additional named arguments given will be assigned
    to as data properties.

    Args:
      lower, upper:
        The lower and upper bounding vertices.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
      dimension:
        The number of dimensions (dimensionality) of
        this Region. must match that number of
        dimensions in the lower and upper vertices.
      kwargs:
        To be assigned as data properties.
    """
    if len(id) == 0:
      id = str(uuid4())
    if dimension <= 0:
      dimension = len(lower)

    assert len(id) > 0
    assert isinstance(lower, List) and all([isinstance(l, Real) for l in lower])
    assert isinstance(upper, List) and all([isinstance(u, Real) for u in upper])
    assert dimension > 0 and len(lower) == len(upper) == dimension

    self.id = id
    self.dimension = dimension
    self.dimensions = [Interval(*i) for i in zip(lower, upper)]
    self.data = {}
    for k, v in kwargs.items():
      self.data[k] = v

  ### Properties: Getters

  @property
  def _instance_invariant(self) -> bool:
    """
    Invariant:
    - dimension == len(dimensions)
    - every items in dimensions is an Interval

    Returns:
      True: If instance invariant holds
      False: Otherwise.
    """
    return all([
      isinstance(self.dimensions, List),
      self.dimension == len(self.dimensions),
      all([isinstance(d, Interval) for d in self.dimensions])
    ])

  @property
  def lower(self) -> List[float]:
    """
    The lower bounding vertex of this Region. Calculate and return a copy of
    the vector that represent the lower bounding values for this Region in
    each dimension.

    Returns:
      The lower bounding vertex of this Region.
    """
    return [d.lower for d in self.dimensions]

  @property
  def upper(self) -> List[float]:
    """
    The upper bounding vertex of this Region. Calculate and return a copy of
    the vector that represent the upper bounding values for this Region in
    each dimension.

    Returns:
      The upper bounding vertex of this Region.
    """
    return [d.upper for d in self.dimensions]

  @property
  def lengths(self) -> List[float]:
    """
    The distances between the lower and upper bounding
    vertices on each dimension.

    Returns:
      List of distances for each dimension.
    """
    return [d.length for d in self.dimensions]

  @property
  def midpoint(self) -> List[float]:
    """
    The point equal distance between the lower and
    upper bounding vertices.

    Returns:
      The point at the midpoint or center of
      Region along all dimensions.
    """
    return [d.midpoint for d in self.dimensions]

  @property
  def size(self) -> float:
    """
    The magnitude size of the Region; length, area, volume.
    Computed by multiply all the dimensional lengths (sides) together.

    Returns:
      The magnitude size of the Region.
    """
    return reduce(lambda x, y: x * y, self.lengths)

  ### Methods: Assignment

  def __getitem__(self, index: Union[int, str]) -> Union[Interval, Any]:
    """
    Retrieves the Interval for associated dimension when index is an int.
    Retrieves the data value for associated data property when index is a str.

    Is syntactic sugar for:
      interval  = self[dimension]
      datavalue = self[datakey]

    Overload Method that wraps:
      self.dimensions[index]
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
      return self.dimensions[index]
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

      self.dimensions[index] = value

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
      'upper': self.upper
    }

    dicttopairs = lambda item: f'{item[0]}={item[1]}'
    dictkvpairs = ', '.join(map(dicttopairs, dictobj.items()))

    return f'{self.__class__.__name__}({dictkvpairs})'

  ### Methods: Queries

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
                for i, d in enumerate(self.dimensions)])

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
                for i, d in enumerate(self.dimensions)])

  def __contains__(self, value: Union['Region', List[float]]) -> bool:
    """
    Determine if the point or Region (value) lies entirely between this
    Region's lower and upper bounding vertices, inclusively. Return True
    if point or Region is entirely within this Region, otherwise False.

    Is syntactic sugar for:
      value in self

    Overload Method that wraps:
      self.contains when value is a point, and
      self.encloses when value is a Region

    Args:
      value:
        The point to test if it lies within this Region's
        bounds, or the other Region to test if it lies
        entirely within this Region's bounds.

    Returns:
      True:   If the point or other Region lies entirely
              within this Region's bounds.
      False:  Otherwise.
    """
    if isinstance(value, Region):
      return self.encloses(value)
    else:
      return self.contains(value)

  def overlaps(self, that: 'Region') -> bool:
    """
    Determine if the given Region overlaps with this Region.
    If the Regions are equal, exact same lower and upper bounding vertices,
    then overlaps. If the Regions are adjacent, then not overlapping.
    To be overlapping, one Region must contains the other's lower or
    upper bounding vertices. As long as all corresponding Intervals for each
    dimension overlap in both Region, then the Regions are overlapping.
    Return True if given Region overlaps with this Region, otherwise False.

    Args:
      that:
        The other Region to test if it overlaps
        with this Region.

    Returns:
      True:   If other Region overlaps with this Region
      False:  Otherwise.

    Examples:

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
    """
    assert isinstance(that, Region)
    assert self.dimension == that.dimension

    return all([d.overlaps(that[i]) for i, d in enumerate(self.dimensions)])

  ### Methods: Equality + Comparison

  def __eq__(self, that: 'Region') -> bool:
    """
    Determine if the given Region equals to this Region.
    If the two Region have the same dimensions (same Intervals; lower and
    upper bounds for all dimensions), then they are equal, otherwise they
    do not equal. Return True if the two Regions are equal, otherwise False.

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
    return that is not None and \
           all([isinstance(that, Region), self.dimension == that.dimension]) and \
           all([d == that[i] for i, d in enumerate(self.dimensions)])

  ### Methods: Generators

  def intersect(self, that: 'Region', linked: Union[bool, str] = False) -> 'Region':
    """
    Compute the overlapping Region between this and that Region.

    Args:
      that:
        The other Region which this Region is to compute
        the overlapping Region with.
      linked:
        Boolean flag whether or not to add a
        data property 'intersect' or a string for how
        the 'intersect' value is computed and assigned.

    linked:
    - 'reference':
        Holds the reference to this Region and
        its intersecting (that) Region
    - 'aggregate':
        Holds all references to the intersecting Regions,
        including previous intersections.

    Returns:
      The overlapping Region
      None: If the Regions do not overlap.

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

    return Region.from_intervals([d.intersect(that[i]) \
                  for i, d in enumerate(self.dimensions)], **data)

  def union(self, that: 'Region', linked: Union[bool, str] = False) -> 'Region':
    """
    Compute the Region that encloses both this and that Region.

    Args:
      that:
        The other Region which this Region is to compute
        the enclosing (union) Region with.
      linked:
        Boolean flag whether or not to add a
        data property 'union' or a string for how
        the 'union' value is computed and assigned.

    linked:
    - 'reference':
        Holds the reference to this Region and
        its enclosing (that) Region
    - 'aggregate':
        Holds all references to the enclosing Regions,
        including previous unions.

    Returns:
      The enclosing Region.

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

    return Region.from_intervals([d.union(that[i]) \
                  for i, d in enumerate(self.dimensions)], **data)

  def project(self, dimension: int, **kwargs) -> 'Region':
    """
    Project this Region to the specified number of dimensions.
    If the given number of dimensions is greater than this Region's
    dimensionality, output a Region with additional dimensions with [0, 0]
    intervals. If the given number of dimensions is less than this Region's
    dimensionality, output a Region with the additional dimensions removed. 
    If the given number of dimensions is equal to this Region's
    dimensionality, outputs a copy of this Region. Additional arguments passed
    through to Region.from_intervals.

    Args:
      dimension:
        The number of dimensions in the output
        projected Region.
      kwargs:
        Additional arguments passed through to
        Region.from_intervals.

    Returns:
      The projected Region.
    """
    assert dimension > 0

    dimensions = [Interval(*astuple(Interval(0, 0) \
                  if d >= self.dimension else self[d])) \
                  for d in range(dimension)]

    return Region.from_intervals(dimensions, **kwargs)

  def random_points(self, npoints: int = 1,
                          randomng: RandomFn = Randoms.uniform()) -> NDArray:
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

    Args:
      npoints:
        The number of points to generate
      randomng:
        The random number generator that dictates
        the distribution of the points generated.

    Returns:
      List of randomly, sampled points drawn
      from within this Regin.
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
    Randomly generate N Regions within this Regions, each with a random size as
    a percentage of the total Region dimensions, bounded by the given size
    percentage Region (enclosed by Region([0, ...], [1, ...])). All subregions
    must have the same number of dimensions as this Region. The default
    distributions for choosing the position of the Region and its size
    percentage are uniform distributions, but can be substituted for other
    distribution or random number generation functions via the `posnrng` and
    `sizerng` parameter. If precision is given, return the randomly generated
    Intervals where the lower and upper bounding values are rounded/truncated
    to the specified precision (number of digits after the decimal point).
    If precision is None, the lower and upper bounding values are of arbitrary
    precision. Additional arguments passed through to Region.from_intervals.

    Args:
      nregions:     The number of Regions to be generated.
      sizepc_range: The size range as a percentage of the
                    total Regions' dimensional length.
      posnrng:      The random number generator for choosing
                    the position of the Region.
      sizerng:      The random number generator for choosing
                    the size of the Region.
      precision:    The number of digits after the decimal
                    point for the lower and upper bounding
                    values, or None for arbitrary precision.
      kwargs:       Additional arguments passed through to
                    Region.from_intervals.

    Returns:
      List of randonly generated Regions
      within this Region.
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

  ### Class Methods: Generators

  @classmethod
  def from_intervals(cls, dimensions: List[Interval],
                          id: str = '', **kwargs) -> 'Region':
    """
    Construct a new Region from the given a list of Intervals.

    Args:
      dimensions:
        List of Intervals for each dimension
        within the Region. A Region of N dimensions
        is created from a list of N Intervals.
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
    assert isinstance(dimensions, List)
    assert all([isinstance(d, Interval) for d in dimensions])

    return cls([d.lower for d in dimensions],
               [d.upper for d in dimensions], id, **kwargs)

  @classmethod
  def from_interval(cls, interval: Interval,
                         dimension: int = 1,
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
  def from_intersect(cls, regions: List['Region'],
                          linked: bool = False,
                          id: str = '') -> Union['Region', None]:
    """
    Constructs a new Region from the intersection of the given Regions.

    Args:
      regions:
        The list of Regions which the overlapping
        Region is generated with.
      linked:
        Boolean flag whether or not to add a
        data property 'intersect' is assigned with
        references to all the intersecting Regions.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.

    Returns:
      The overlapping Region.
      None: If the Regions do not overlap.
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
  def from_union(cls, regions: List['Region'],
                      linked: bool = False, id: str = '') -> 'Region':
    """
    Constructs a new Region from the union of the given Regions.

    Args:
      regions:
        The list of Regions which the enclosing
        Region is generated with.
      linked:
        Boolean flag whether or not to add a
        data property 'union' is assigned with
        references to all the enclosing Regions.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.

    Returns:
      The enclosing Region.
    """
    assert isinstance(regions, List) and len(regions) > 1
    assert all([isinstance(r, Region) for r in regions])
    assert all([regions[0].dimension == r.dimension for r in regions])

    dimensions = zip(*list(map(lambda r: r.dimensions, regions)))
    dimensions = [Interval.from_union(list(d)) for d in dimensions]
    data = {'union': regions.copy()} if linked else {}

    return cls.from_intervals(dimensions, id, **data)

  ### Class Methods: (De)serialization

  @classmethod
  def to_object(cls, object: 'Region', format: str = 'json', **kwargs) -> Any:
    """
    Generates an object (dict, list, or tuple) from the given Region object
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
    assert isinstance(object, Region)

    fieldnames = ['id', 'dimension', 'dimensions', 'data']

    if 'compact' in kwargs and kwargs['compact']:
      dictobj = dict(map(lambda f: (f, getattr(object, f)), fieldnames))

      if 'data' in dictobj:
        if dictobj['data'] is object.data:
          dictobj['data'] = dictobj['data'].copy()
        if 'intersect' in dictobj['data']:
          dictobj['data']['intersect_'] = list(map(lambda r: r.id, dictobj['data']['intersect']))
          del dictobj['data']['intersect']
        if 'union' in dictobj['data']:
          dictobj['data']['union_'] = list(map(lambda r: r.id, dictobj['data']['union']))
          del dictobj['data']['union']
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
    - dimension (int), lower (float or List[float]) and
      upper (float or List[float])

    Note:
    - Interval-equivalent means parseable by
      Interval.from_object.

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
    - A List of objects that are parseable by
      Interval.from_object, to be passed to the
      from_intervals method.
    - A Tuple containing 2 values:
      - An int as the number of dimension,
        to be passed to from_interval and
      - An object that is parseable by the
        Interval.from_object method.

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
      return cls.from_intervals(list(map(Interval.from_object, object)), id)
    elif isinstance(object, Tuple):
      assert len(object) == 2
      assert isinstance(object[0], int) and 0 < object[0]
      return cls.from_interval(Interval.from_object(object[1]), object[0], id)
    else:
      raise ValueError('Unrecognized Region representation')
