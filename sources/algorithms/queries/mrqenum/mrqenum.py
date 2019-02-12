#!/usr/bin/env python

"""
Enumeration Query of Multiple Intersecting Regions -- Implementation Agnostic

Perform enumeration of intersecting Regions from a subsetted set of Regions.
The enumeration outputs an Iterator of the intersecting Regions as tuple of
Region intersection and RegionIntns in order of the number of intersecting
Regions involved. Binds together multiple implementations and algorithms into
common single, abstracted interface.

Classes:
- MRQEnum
"""

from typing import Union

from ..rqenum import RQEnum
from .bynxgraph import MRQEnumByNxGraph
from .byrcsweep import MRQEnumByRCSweep


class MRQEnum(RQEnum):
  """
  Static Class

  Enumeration Query of Multiple Intersecting Regions
  Regardless of Implementation

  Perform enumeration of intersecting Regions from a subsetted set of Regions.
  The enumeration outputs an Iterator of the intersecting Regions as tuple of
  Region intersection and RegionIntns in order of the number of intersecting
  Regions involved. Binds together multiple implementations and algorithms into
  common single, abstracted interface.

  Extends:
    RQEnum

  Implementations:
  - naive
  - slig

  Example:
  >>> enumerator = MRQEnum.get('naive').prepare(regions, subset)
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get and prepare:
  >>> enumerator = MRQEnum.get('slig', regions, subset) # constructs graph, or takes
  >>> enumerator = MRQEnum.get('slig', nxgraph, subset) # one preconstructed
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get results directly:
  >>> results = MRQEnum.results('naive', regions, subset)
  >>> results = MRQEnum.results('slig', regions, subset)
  >>> results = MRQEnum.results('slig', nxgraph, subset)

  Class Attributes:
    algorithms:
      The mapping of algorithm names to
      algorithm implementation classes.
  """
  algorithms = {
    'naive': MRQEnumByRCSweep,
    'slig':  MRQEnumByNxGraph
  }
