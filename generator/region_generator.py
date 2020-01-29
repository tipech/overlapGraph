#!/usr/bin/env python

"""
Region Generator class

Implements the RegionGenerator class, a class that handles random generation
of regions.


Classes:
- RegionGenerator
"""
import json
from typing import Callable, List, Union
from numbers import Real
from io import TextIOBase
import random


from ..slig.datastructs import Region, Interval, RegionSet
from .random_functions import Randoms

class RegionGenerator():
  """
  Singleton Class.

  Random generation of regions or graphs.
  """
  def __init__(self, bounds: Union[Region,Interval] = None,
               dimension = None, sizepc: Union[Region,Interval,Real] = 0.05,
               posnrng: Union[Callable,List[Callable]] = Randoms.uniform(),
               sizerng: Union[Callable,List[Callable]] = Randoms.uniform(),
               square = False):
    """
    Initialize the data generator with user-specified parameters.

    Args:
      sizepc:     The size range as a percentage of the
                  total Regions' dimensional length.
      posnrng:    The random number generator or list of
                  random number generator options
                  for choosing the position of the Region.
      sizerng:    The random number generator or list of
                  random number generator options
                  for choosing the size of the Region.
      precision:  The number of digits after the decimal
                  point for the lower and upper bounding
                  values, or None for arbitrary precision.

    Returns:
      A RegionGenerator singleton object.
    """

    # bounds & dimensions pc init
    if bounds is not None:
      if isinstance(bounds, Interval):
        bounds = Region.from_interval(bounds, 1)
      else:
        assert isinstance(bounds, Region)

      if dimension is not None:
        assert dimension == bounds.dimension

      self.dimension = bounds.dimension
      self.bounds = bounds

    else:
      if dimension == None:
        dimension = 2

      assert dimension > 0

      self.dimension = dimension
      self.bounds = Region.from_interval(Interval(0,1000), dimension)

    # size pc init
    ndunit_region = Region.from_interval(Interval(0,1), self.dimension)

    if sizepc is None:
      sizepc = ndunit_region
    if isinstance(sizepc, Real):
      sizepc = Region.from_interval(Interval(0,sizepc), self.dimension)
    elif isinstance(sizepc,Interval):
      sizepc = Region.from_interval(sizepc, self.dimension)

    assert isinstance(sizepc, Region)
    assert sizepc.dimension == self.dimension
    assert ndunit_region.encloses(sizepc)

    self.sizepc = sizepc

    # random functions init
    if isinstance(posnrng, Callable):
      posnrng = [posnrng]
    if isinstance(sizerng, Callable):
      sizerng = [sizerng]


    for rng in [posnrng, sizerng]:
      assert (isinstance(rng, List) and
              all(isinstance(f, Callable) for f in rng))

    self.posnrng = posnrng
    self.sizerng = sizerng

    self.square = square
    

  def get_region(self):
    """Randomly generate a single Region according to generator parameters"""

    sizerng = random.choice(self.sizerng)
    posnrng = random.choice(self.posnrng)

    window_size = [self.bounds.upper[d] - self.bounds.lower[d]
      for d in range(self.dimension)]

    if self.square:
      side_size = self.sizerng[0](self.sizepc.lower[0] * window_size[0],
      self.sizepc.upper[0] * window_size[0])

      size = [side_size for d in range(self.dimension)]
    else:
      size = [self.sizerng[d](self.sizepc.lower[d] * window_size[d],
        self.sizepc.upper[d] * window_size[d])
        for d in range(self.dimension)]
    
    lower = [posnrng(self.bounds.lower[d], self.bounds.upper[d] - size[d], d)
            for d in range(self.dimension)]

    upper = [lower[d] + size[d] for d in range(self.dimension)]
    
    return Region(lower, upper)

    

  def get_regionset(self, nregions: int) -> RegionSet:
    """Randomly generate N Regions according to generator parameters."""

    regionset = RegionSet(bounds=self.bounds)
    for r in range(0, nregions):
      regionset.add(self.get_region())

    return regionset


  def store_regionset(self, nregions: int, file: Union[str,TextIOBase]):
    """Randomly generate N Regions and store results to file."""

    regionset = RegionSet(bounds=self.bounds)
    for r in range(nregions):
      regionset.add(self.get_region())

    if isinstance(file, str):
      fp = open(file, "w+")
    elif file.writeable():
      fp = file
    else:
      raise ValueError(f'Unsupported file format')

    try:
      regionset.to_output(fp)

    finally:
      fp.close()
      