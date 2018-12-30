#!/usr/env/python

"""
One-Pass Sweep-line Algorithm for RegionSet

This script implements an one-pass sweep-line algorithm over a set of Regions.
Implements RegionSweep class that executes the specific details and actions
of the sweep-line algorithm, when encountering a Begin or End event.

Classes:
- RegionSweep
"""

from typing import Any, Dict, Iterator, List, Tuple

from sources.algorithms.sweepln.sweepln import Sweepln, SweepRunner
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.regiontime import RegionEvent, RegionEvtKind, RegionTimeln
from sources.datastructs.shapes.region import Region, RegionPair


class RegionSweep(SweepRunner[Region, List[RegionPair]]):
  """
  Class for implementing an one-pass sweep-line algorithm over a set of
  Regions. Binds to and is evaluated by the one-pass sweep-line algorithm
  along a dimension on the set of Regions.

  Attributes:
    dimension:  The dimension to evaluate sweep-line over.
    actives:    The active Regions during sweep-line.
    overlaps:   The resulting pairwise overlaps.

  Properties:
    regions:    The RegionSet to evaluate sweep-line over.

  Methods:
    Special:    __init__
    Instance:   findoverlaps, addoverlap,
                onbegin, onend

  Inherited from SweepRunner:

    Attributes:
      id:       The unique identifier for this SweepRunner.
      events:   Mapping of event kinds to event callbacks.
      sweepln:  The Sweepln algorithm for which its binded.
      timeline: The Timeline to evaluate sweep-line over.
      running:  Boolean flag for whether or not the
                algorithm is currently running.

    Properties:
      binded:
        Whether or not this SweepRunner is binded to a
        Sweepln algorithm. True if it is binded, False 
        otherwise.
      initialized:
        Whether or not this SweepRunner has been
        initialized for evaluation. True if it is
        initialized, False otherwise.
    
    Methods:
      Special:  __init__
      Instance: bind, unbind, results, hasevent,
                onevent, oninit, onfinal

    Overridden Methods:
      Special:  __init__
      Instance: results, oninit, onfinal
  """
  dimension: int
  actives  : Dict[str, Region]
  overlaps : List[RegionPair]

  def __init__(self, id: str = ''):
    """
    Initialize this RegionSweep with the default values.

    Args:
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
    """
    self.dimension = None

    SweepRunner.__init__(self, {
      RegionEvtKind.Begin: 'onbegin',
      RegionEvtKind.End: 'onend'
    }, id)

  ### Properties: Getters

  @property
  def regions(self) -> RegionSet:
    """
    Returns the set of Regions associated with the RegionSweep.

    Returns:
      The linked RegionSet object.
    """
    assert isinstance(self.timeline, RegionTimeln)

    if self.timeline != None:
      return self.timeline.regions
    else:
      return None

  ### Methods: Overlaps

  def findoverlaps(self, region: Region) -> Iterator[RegionPair]:
    """
    Return an iterator over all the pairs of overlaps between the
    given Region and the currently active Regions, as RegionPairs.

    This method should be overridden in subclasses to implement,
    the finding of overlaps using more efficient means, such as:
    via an Interval tree.

    Args:
      region:   The Region to find pairs of overlaps with
                currently active Regions, as RegionPairs.

    Returns:
      An iterator over all the pairs of overlaps between
      the Region and currently active Regions.
    """
    for _, activeregion in self.actives.items():
      if region.overlaps(activeregion):
        yield (activeregion, region)

  def addoverlap(self, regionpair: RegionPair):
    """
    Add the given pair of Regions to the list of overlaps.
    This method should be overridden in subclasses to implement:

    - The addition of a edge in the intersection graph
      between the given region pair and labelling of the
      edge with additional information,
    - The addition of a branch in the interval tree for the
      given region pair and labelling of the branch with
      additional information.

    Args:
      regionpair:
        The pair of Regions to add as overlaps.
    """
    self.overlaps.append(regionpair)

  ### Methods: Results

  def results(self) -> List[RegionPair]:
    """
    Returns the list of overlapping Regions found in the RegionSet
    using the sweep-line algorithm.

    Returns:
      The list of overlapping Regions.
    """
    return self.overlaps

  ### Methods: Event Callbacks

  def oninit(self, **kwargs):
    """
    Initialize the evaluation of the RegionSet in the RegionSweep
    with the given dimensions. This method should be overridden in
    subclasses to implement:

    - The creation of nodes in the intersection
      graph for each Region.
    - The creation of the interval tree root in
      preparation for the addition of branches and
      leaves associated with the overlaps.

    Args:
      kwargs:
        Additional arguments

    kwargs:
      dimension:
        The dimension to evaluate sweep-line over.
    """
    assert self.binded and not self.initialized

    dimension = kwargs['dimension'] if 'dimension' in kwargs else 0

    assert isinstance(dimension, int)
    assert 0 <= dimension < self.regions.dimension

    self.dimension = dimension
    self.actives   = {}
    self.overlaps  = []

    SweepRunner.oninit(self)

  def onbegin(self, event: RegionEvent, **kwargs):
    """
    When a Begin event is encountered in the RegionSweep evaluation, 
    this method is invoked with that RegionEvent. Invokes findoverlaps and
    addoverlap methods from here. Adds the newly active Region to the
    set of active Regions.

    Args:
      event:
        The beginning event when encountered
        in the RegionSweep evaluation.
      kwargs:
        Additional arguments (unused)
    """
    assert isinstance(event, RegionEvent)
    assert self.binded and self.initialized
    
    region = event.context
    assert region.id not in self.actives

    for regionpair in self.findoverlaps(region):
      self.addoverlap(regionpair)

    self.actives[region.id] = region

  def onend(self, event: RegionEvent, **kwargs):
    """
    When an End event is encountered in the RegionSweep evaluation, this
    method is invoked with that RegionEvent. Removes the ending Region from
    to the set of active Regions.

    Args:
      event:
        The ending event when encountered
        in the RegionSweep evaluation.
      kwargs:
        Additional arguments (unused)
    """
    assert isinstance(event, RegionEvent)
    assert self.binded and self.initialized

    region_id = event.context.id
    assert region_id in self.actives
    del self.actives[region_id]

  def onfinal(self, **kwargs):
    """
    Finalize the RegionSweep for the Sweepln algorithm.
    When the Sweepln evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this RegionSweep.
    Sets the result value with the computed overlapping Regions.

    This method should be overridden in subclasses to implement:
    
    - Any cleanup or finalization routines for data 
      structures, such as intersection graphs and
      interval trees
    - Initialize the next pass on a different dimension
      for multi-pass single-threaded versions of the 
      sweep-line algorithm.
    """
    assert self.binded and self.initialized
    assert len(self.actives) == 0

    self.dimension = None
    SweepRunner.onfinal(self)
