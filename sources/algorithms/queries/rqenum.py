#!/usr/bin/env python

"""
Abstract Region Query -- Implementation Agnostic

Binds together multiple implementations and algorithms into
common single, abstracted interface.

Classes:
- RQEnum
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Type, Union

from sources.core import RegionSet


class RQEnum(metaclass=ABCMeta):
  """
  Abstract Static Class

  Binds together multiple implementations and algorithms into
  common single, abstracted interface.

  Class Attributes:
    algorithms:
      The mapping of algorithm names to
      algorithm implementation classes.
  """
  algorithms = {}

  @classmethod
  def get(cls, alg: str, *args, **kwargs):
    """
    Retrieves and returns the specified algorithm with given name.
    Returns the algorithm's implementation class.
    If additional arguments are given, passes the arguments to the prepare
    class method of the algorithm's implementation class, and returns the
    evaluator function for evaluating the query instead.

    Args:
      alg:
        The name of the algorithm to retrieve.
      args, kwargs:
        Additional arguments to be passed to the
        'prepare' class method of the algorithm's
        implementation class.

    Returns:
      The algorithm's implementation class, or
      a function to evaluate the algorithm and
      compute the resulting value.
    """
    assert alg in cls.algorithms
    algorithm = cls.algorithms[alg]
    assert callable(getattr(algorithm, 'prepare'))

    return algorithm if len(args) + len(kwargs) == 0 \
                     else algorithm.prepare(*args, **kwargs)

  @classmethod
  def results(cls, alg: str, ctx: Any, *args, **kwargs) -> RegionSet:
    """
    Compute and return the results of the query with the specified
    algorithm with the given context object (must have the 'dimension'
    attribute).

    Args:
      alg:
        The name of the algorithm to retrieve.
      ctx:
        The context object.
      args, kwargs:
        Additional arguments to be passed to the
        'prepare' class method of the algorithm's
        implementation class.

    Returns:
      The resulting values for the query evaluation.
    """
    assert alg in cls.algorithms
    assert ctx is not None and hasattr(ctx, 'dimension')

    results = RegionSet(dimension=ctx.dimension)
    enumerator = cls.get(alg, ctx, *args, **kwargs)
    for region, _ in enumerator():
      results.add(region)

    return results
