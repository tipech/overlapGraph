#!/usr/bin/env python

"""
Enumeration Query of Single Intersecting Regions -- Implementation Agnostic

Perform enumeration of intersecting Regions involving a specific Region.
The enumeration outputs an Iterator of the intersecting Regions as tuple of
Region intersection and RegionIntns in order of the number of intersecting
Regions involved. Binds together multiple implementations and algorithms into
common single, abstracted interface.

Classes:
- SRQEnum
"""

from typing import Union

from ..rquery import RegionQuery
from .bynxgraph import SRQEnumByNxGraph
from .byrcsweep import SRQEnumByRCSweep


class SRQEnum(RegionQuery):
  """
  Static Class

  Enumeration Query of Single Intersecting Regions
  Regardless of Implementation

  Perform enumeration of intersecting Regions involving a specific Region.
  The enumeration outputs an Iterator of the intersecting Regions as tuple of
  Region intersection and RegionIntns in order of the number of intersecting
  Regions involved. Binds together multiple implementations and algorithms into
  common single, abstracted interface.

  Extends:
    RegionQuery

  Implementations:
  - naive
  - slig

  Example:
  >>> enumerator = SRQEnum.get('naive').prepare(regions, query)
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get and prepare:
  >>> enumerator = SRQEnum.get('slig', regions, query) # constructs graph, or takes
  >>> enumerator = SRQEnum.get('slig', nxgraph, query) # one preconstructed
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get results directly:
  >>> results = SRQEnum.results('naive', regions, query)
  >>> results = SRQEnum.results('slig', regions, query)
  >>> results = SRQEnum.results('slig', nxgraph, query)

  Class Attributes:
    algorithms:
      The mapping of algorithm names to
      algorithm implementation classes.
  """
  algorithms = {
    'naive': SRQEnumByRCSweep,
    'slig':  SRQEnumByNxGraph
  }
