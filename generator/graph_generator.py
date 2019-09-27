#!/usr/bin/env python

"""
Graph Generator class

Implements the GraphGenerator class, a class that handles random generation
of RIG graphs.


Classes:
- GraphGenerator
"""
import json
from typing import Callable, List, Union
from numbers import Real
from io import TextIOBase

from slig.datastructs import Region, Interval
from generator.random_functions import Randoms

class GraphGenerator():
  """
  Singleton Class.

  Random generation of regions or graphs.
  """
  def __init__(self, bounds: Union[Region,Interval] = None,
               dimensions = None, sizepc: Union[Region,Interval,Real] = 0.05,
               posnrng: Union[Callable,List[Callable]] = Randoms.uniform(),
               sizerng: Union[Callable,List[Callable]] = Randoms.uniform(),
               square = False):
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
      A GraphGenerator singleton object.
    """
    pass