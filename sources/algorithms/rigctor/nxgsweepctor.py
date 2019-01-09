#!/usr/bin/env python

"""
Regional Intersection Graph (RIG) Construction by
One-pass Sweepline Algorithm -- NetworkX

This script implements the NxGraphSweepCtor (or one-pass sweep-line regional
intersection graph construction algorithm). This algorithm builds an
undirected, labelled graph of all the pair-wise intersections or overlapping
regions between a collection of regions with the same dimensionality. The
graph representation is implemented as a NetworkX graph.

Classes:
- NxGraphSweepCtor
"""

from typing import Tuple, Union

from sources.algorithms.sweepln.regionsweep import RegionSweepEvtKind
from sources.datastructs.abstract.pubsub import Event, Subscriber
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region, RegionPair


class NxGraphSweepCtor(Subscriber[Union[Region, RegionPair]]):
  """
  Implementation of regional intersection graph construction based on a one-
  pass sweep-line algorithm. This algorithm builds an undirected, weighted
  graph of all the pair-wise intersections or overlapping regions within a
  RegionSet, through a subscription to RegionSweep.
  The graph representation is implemented as a NetworkX graph.

  Attributes:
    G:
      The NetworkX graph representation of
      intersecting Regions.
    regions:
      The RegionSet to construct the Region
      intersection graph from.

  Properties:
    results:
      The resulting NetworkX graph of
      intersecting Regions.

  Methods:
    Special:  __init__
    Instance: on_intersect

  Inherited from Subscriber:
    Attributes:
      events:
        The registered Event types (kind).
        If None, no register Event types.
      eventmapper:
        A lambda method that maps each Event to a method
        name for a specific event handler.
      strict:
        Boolean flag whether or not to raise an exception
        when Event handler not found. True, raises
        exception; False, otherwise. Default: False.

    Methods:
      Special:  __init__
      Instance: on_next, on_completed, on_error

    Overridden Methods:
      Special:  __init__
  """
  regions: RegionSet
  G: NxGraph

  def __init__(self, regions: RegionSet):
    """
    Initialize the intersection graph construction
    using the one-pass sweep-line algorithm.
    Sets the events as RegionSweepEvtKind.

    Args
      regions:
        The RegionSet to construct the Region
        intersection graph from.
    """
    Subscriber.__init__(self, RegionSweepEvtKind)

    self.regions = regions
    self.G = NxGraph(self.regions.dimension)

    for region in self.regions:
      self.G.put_region(region)

  ### Properties

  @property
  def results(self) -> NxGraph:
    """
    The resulting NetworkX graph of intersecting Regions.
    Alias for: self.G.

    Returns:
      The newly constructed NetworkX graph of
      intersecting Regions.
    """
    return self.G

  ### Methods: Event Handlers

  def on_intersect(self, event: Event[RegionPair]):
    """
    Handle Event when sweep-line algorithm encounters the two or more 
    Regions intersecting. Add the given Event's context, pairs of Regions,
    to the intersection graph as an edge. The intersection Region is added
    to the edge as an data attribute.

    Args:
      event:
        The intersecting Regions Event.
    """
    assert event.kind == RegionSweepEvtKind.Intersect
    assert isinstance(event.context, Tuple) and len(event.context) == 2
    assert all([isinstance(r, Region) for r in event.context])

    self.G.put_overlap(event.context)
