#!/usr/bin/env python

"""
Enumeration of all Intersecting Regions -- Implementation Agnostic

The enumeration outputs an Iterator of the intersecting Regions as tuple of
Region intersection and RegionIntns in order of the number of intersecting
Regions involved. Binds together multiple implementations and algorithms into
common single, abstracted interface.

Classes:
- Enumerate
"""

from typing import Union

from ..rqenum import RQEnum
from .bynxgraph import EnumerateByNxGraph
from .byrcsweep import EnumerateByRCSweep


class Enumerate(RQEnum):
  """
  Static Class

  Enumeration of all Intersecting Regions Regardless of Implementation

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
  >>> enumerator = Enumerate.get('naive').prepare(regions)
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get and prepare:
  >>> enumerator = Enumerate.get('slig', regions) # constructs graph, or takes
  >>> enumerator = Enumerate.get('slig', nxgraph) # one preconstructed
  >>> results = RegionSet(dimension=regions.dimension)
  >>> for region, intersect in enumerator():
  ...   results.add(region)

  Or get results directly:
  >>> results = Enumerate.results('naive', regions)
  >>> results = Enumerate.results('slig', regions)
  >>> results = Enumerate.results('slig', nxgraph)

  Class Attributes:
    algorithms:
      The mapping of algorithm names to
      algorithm implementation classes.
  """
  algorithms = {
    'naive': EnumerateByRCSweep,
    'slig':  EnumerateByNxGraph
  }
