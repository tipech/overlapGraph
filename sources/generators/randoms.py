#!/usr/bin/env python

#
# generators/randoms.py - Random Number Generators
#
# This script implements the Randoms class, a static class
# that provides factory methods that each return Callable (lambdas)
# that are preconfigured to generate random values based on a
# particular distribution or random number generation function.
# The only missing parameters is the lower and upper bounds of the
# values generated and the sample size of the output.
#
from typing import List, Dict, Union, Callable
from numpy import random, ndarray

ShapeSize = Union[None,int,List[int]]
NDArray   = ndarray
RandomFn  = Callable[[float, float, ShapeSize], NDArray]

class Randoms:
  """
  Static class that provides factory methods that each return Callable
  (lambdas) that are preconfigured to generate random values based on a
  particular distribution or random number generation function. The only
  missing parameters is the lower and upper bounds of the values generated and
  the sample size of the output.

  Class Methods: uniform, triangular
  """

  @classmethod
  def get(cls, name: str, **args) -> RandomFn:
    """
    Returns a function that draws samples from the specified distribution
    or random number generation function that corresponds with the given
    method name. Passes the given arguments as parameter for that
    factory method.

    :param name:
    :param args:
    """
    return getattr(cls, name)(**args)

  @classmethod
  def uniform(cls) -> RandomFn:
    """
    Returns a function that draws samples from a uniform distribution.
    Samples are uniformly distributed over the half-open interval [low, high)
    (includes low, but excludes high). In other words, any value within the given
    interval is equally likely to be drawn by uniform.
    """
    return lambda size = 1, low = 0, high = 1: \
      random.uniform(low, high, size)

  @classmethod
  def triangular(cls, mode: float) -> RandomFn:
    """
    Returns a function that draws samples from the triangular distribution over the
    interval [left, right]. The triangular distribution is a continuous probability
    distribution with lower limit left, peak at mode, and upper limit right. Unlike
    the other distributions, these parameters directly define the shape of the
    probability distribution function (pdf).
    """
    return lambda size = 1, left = 0, right = mode: \
      random.triangular(left, mode, right, size)
