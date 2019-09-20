
#!/usr/bin/env python

"""
Data Generator class Class

Implements the Generator class, a class that handles random generation of
regions or graphs.


Classes:
- Generator
"""
from sources.helpers import NDArray, RandomFn, Randoms

class Generator():
  """
  Singleton Class.

  Random generation of regions or graphs.
  """
  def __init__(self, space: Number,sizepc: None,
               posnrng: Union[RandomFn,List[RandomFn]] = Randoms.uniform(),
               sizerng: Union[RandomFn,List[RandomFn]] = Randoms.uniform(),
               precision: int = None) -> Generator:
  """
  Initialize the data generator with user-specified parameters.

  Args:
    sizepc:     The size range as a percentage of the
                total Regions' dimensional length.
    posnrng:    The random number generator or list of
                random number generator (per dimension)
                for choosing the position of the Region.
    sizerng:    The random number generator or list of
                random number generator (per dimension)
                for choosing the size of the Region.
    precision:  The number of digits after the decimal
                point for the lower and upper bounding
                values, or None for arbitrary precision.

  Returns:
    A Generator singleton object.
  """


    self.arg = arg
    

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

def random_regions(self, nregions: int = 1, 
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
    nregions:   The number of Regions to be generated.
    
    kwargs:     Additional arguments passed through to
                Region.from_intervals.

  Returns:
    List of randonly generated Regions
    within this Region.
  """
  ndunit_region = Region([0] * self.dimension, [1] * self.dimension)
  if sizepc == None:
    sizepc = ndunit_region

  assert isinstance(sizepc, Region) and self.dimension == sizepc.dimension
  assert ndunit_region.encloses(sizepc)

  if isinstance(posnrng, Callable):
    posnrng = [posnrng] * self.dimension
  if isinstance(sizerng, Callable):
    sizerng = [sizerng] * self.dimension

  for rng in [posnrng, sizerng]:
    assert isinstance(rng, List) and \
           all(isinstance(f, Callable) for f in rng) and \
           len(rng) == self.dimension

  regions = []
  for _ in range(nregions):
    region = []
    for i, d in enumerate(self.dimensions):
      dimension = d.random_intervals(1, sizepc[i], posnrng[i], sizerng[i], precision)[0]
      region.append(dimension)
    regions.append(Region.from_intervals(region, **kwargs))
  return regions