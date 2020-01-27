#!/usr/bin/env python

"""
Random Number Generators

Implements the Randoms class, a static class that provides factory methods
that each return Callable (lambdas) that are preconfigured to generate random
values based on a particular distribution or random number generation
function. The only missing parameters is the lower and upper bounds of the
values generated and the sample size of the output.

Types:
- ShapeSize
- NDArray
- RandomFn

Classes:
- Randoms
"""

from typing import Callable, Dict, List, Union
from functools import partial

import random



class Randoms:
  """
  Static class that provides factory methods that each return Callable
  (lambdas) that are preconfigured to generate random values based on a
  particular distribution or random number generation function. The only
  missing parameters is the lower and upper bounds of the values generated
  and the sample size of the output.
  """

  @classmethod
  def get(cls, name: str, **kwargs) :
    """
    Returns a function that draws samples from the specified distribution or
    random number generation function that corresponds with the given method
    name. Passes the given arguments as parameter for that factory method.

    Args:
      name:
        The name of random number generator for
        factory method that generated random
        number generators.
      kwargs:
        arguments as parameter for that factory method.

    Returns:
      The factory method that generated random
      number generators.

      Args:
        size:
          The number of random values to be generated.
        lower:
          The lower bounding value of the range from
          which random values are to be generated.
        upper:
          The upper bounding value of the range from
          which random values are to be generated.

      Returns:
        The randomly generated values.
    """
    return getattr(cls, name)(**kwargs)


  @classmethod
  def list(cls) -> List[str]:
    """
    Returns the list of available random number
    generators (distributions).

    Returns:
      The list of available random number
      generators (distributions).
    """
    excluded = ['get', 'list']
    israndng = lambda f: all([callable(getattr(cls, f)), f not in excluded,
                              not f.startswith('_')])

    return [f for f in dir(cls) if israndng(f)]

  ### Class Methods: Random Number Generators


  @classmethod
  def uniform(cls) :
    """
    Returns a function that draws samples from a uniform distribution.
    Samples are uniformly distributed over the half-open interval [low, high)
    (includes low, but excludes high). In other words, any value within the
    given interval is equally likely to be drawn by uniform.

    Returns:
      A factory function that draws samples
      from a uniform distribution.
    """
    def uniform_rng(lower: float = 0, upper: float = 1, d: int = None):
      return random.uniform(lower, upper)

    return uniform_rng


  @classmethod
  def triangular(cls, mode: float = 0.5) :
    """
    Returns a function that draws samples from the triangular distribution
    over the interval [left, right]. The triangular distribution is a
    continuous probability distribution with lower limit left, peak at mode,
    and upper limit right. Unlike the other distributions, these parameters
    directly define the shape of the probability distribution function (pdf).

    Args:
      mode:
        The peak value of the triangular
        distribution as a percentage of the
        total length.

    Returns:
      A factory function that draws samples
      from a triangular distribution.
    """
    def triangular_rng(left: float = 0, right: float = 1, d: int = None):
      return random.triangular(left, right, (right - left)*mode + left)

    return triangular_rng


  @classmethod
  def gauss(cls, mean: float = 0.5, sigma: float = 0.2) :
    """
    Returns a function that draws samples from the gaussian distribution
    over the interval [left, right]. The gaussian distribution is a
    continuous probability distribution with lower limit left, mean at mean,
    standard deviation sigma and upper limit right.

    Args:
      mean:
        The mean value of the gaussian
        distribution as a percentage of the
        total length.
      sigma:
        The standard deviation of the gaussian
        distribution as a percentage of the
        total length.

    Returns:
      A factory function that draws samples
      from a triangular distribution.
    """
    def gauss_rng(left: float = 0, right: float = 1, d: int = None):
      return max(left, min(right,
        random.gauss((right - left)*mean + left, (right - left)*sigma)))

    return gauss_rng
      

  @classmethod
  def bimodal(cls, mean1: float = 0.2, sigma1: float = 0.1,
                        mean2: float = 0.8, sigma2: float = 0.1) :
    """
    Returns a function that draws samples from a bimodal gauss distribution
    over the interval [left, right]. This distribution is a combination
    of two gaussian probability distributions with lower limit left, upper
    limit right, and two respective mean and sigma vaules.

    Args:
      mean1, mean2:
        The mean values of the gaussian
        distributions as a percentage of the
        total length.
      sigma1, sigma2:
        The standard deviations of the gaussian
        distributions as a percentage of the
        total length.

    Returns:
      A factory function that draws samples
      from a triangular distribution.
    """
    def bimodal_rng(left: float = 0, right: float = 1, d: int = None):
      return max(left, min(right, random.choice(
        [random.gauss((right - left)*mean1 + left, (right - left)*sigma1),
         random.gauss((right - left)*mean2 + left, (right - left)*sigma2)])
      ))

    return bimodal_rng
      

  @classmethod
  def hotspot(cls, d: int, n: int, min_mean: float=0, max_mean: float=1,
      min_sigma: float = 0.05, max_sigma: float = 0.2) :
    """
    Returns a function that draws samples from a gauss hotspot distribution
    over the interval [left, right]. This distribution is a combination
    of n gaussian probability distributions (hotspots) with lower limit left,
    upper limit right, and mean and sigma vaules between min and max.

    Args:
      n:
        Number of hotspots
      d:
        The number of dimensions
      min_mean, max_mean:
        Minimum and maximum mean values of the
        gaussian distributions as a percentage
        of the total length.
      min_sigma, min_sigma:
        Minimum and maximum standard deviations
        of the gaussian distributions as a
        percentage of the total length.

    Returns:
      A factory function that draws samples
      from a triangular distribution.
    """
    hotspots = []
    for h in range(n):

      # generate list means and sigma for each hotspot
      mean = [random.uniform(min_mean, max_mean) for i in range(d)]
      sigma = [random.uniform(min_sigma, max_sigma) for i in range(d)]

      def hotspot_rng(left: float = 0, right: float = 1, d: int = None, 
        mean = None, sigma = None):
        if d is None:
          raise ValueError("Need to provide current dimension!")

        return max(left, min(right, random.gauss(
          (right - left)*mean[d] + left, (right - left)*sigma[d])))

      hotspots.append(partial(hotspot_rng, mean=mean, sigma=sigma))

    return hotspots
