#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm

This script implements a generalized version of a single-pass
sweepline algorithm. Implements SweeplnAlg and SweeplnRT classes, where
the SweeplnRT (the runtime) drives the evaluation by initializing each
SweeplnAlgs' oninit methods, looping over the sorted Events and executing
each SweeplnAlgs' onbegin and onend handlers, and finally, invoking each
SweeplnAlgs' onfinalize methods. The SweeplnAlg (evaluator) is a base
class for implementations that implement these handlers and maintain the
necessary, associated interval state of the evaluation.
"""

from typing import Any, Dict, Iterable, List, Tuple

from sources.datastructs.region import Region, RegionPair
from sources.datastructs.regionset import RegionSet
from sources.datastructs.timeline import Event, EventKind


class SweeplnAlg:
  """
  Base class for implementing a SweeplnAlg (evaluator) that is
  binded to and evaluated when the SweeplnRT evaluates a single-pass,
  sweepline along a dimension on a set of Regions.

  Properties:           runtime, regionset, dimension, actives, overlaps
  Computed Properties:  binded, initialized
  Special Methods:      __init__
  Methods:              bind, unbind, findoverlaps, addoverlap,
                        oninit, onbegin, onend, onfinalize
  """
  runtime   : 'SweeplnRT'
  regionset : RegionSet
  dimension : int
  actives   : Dict[str, Region]
  overlaps  : List[RegionPair]

  def __init__(self):
    """Initialize this SweeplnAlg with None values."""
    self.runtime = None
    self.regionset = None
    self.dimension = None

  @property
  def binded(self) -> bool:
    """
    Determine if this SweeplnAlg is binded to a SweeplnRT.
    Return True if it is binded otherwise False.
    """
    return isinstance(self.runtime, SweeplnRT)

  @property
  def initialized(self) -> bool:
    """
    Determine if this SweeplnAlg has been initialized for evaluation.
    Return True if it is initialized otherwise False.
    """
    return isinstance(self.dimension, int)

  def bind(self, runtime: 'SweeplnRT', unbind: bool = False):
    """
    Bind or attach this SweeplnAlg to the given SweeplnRT.
    If the unbind flag is True, unbinds the previous SweeplnRT if this
    SweeplnAlg is currently binded to it.

    :param runtime:
    :param unbind:
    """
    if unbind:
      self.unbind()
    else:
      assert not self.binded

    self.runtime = runtime
    self.regionset = runtime.regionset

  def unbind(self):
    """
    Unbind or detach this SweeplnAlg from its currently 
    atteched SweeplnRT.
    """
    if self.binded:
      self.runtime = None
      self.regionset = None

  def findoverlaps(self, region: Region) -> Iterable[RegionPair]:
    """
    Given a Region, return an iterator for iterating over
    all the pairs of overlaps between the given Region and the
    currently active Regions, as RegionPairs.

    This method should be overridden in subclasses to implement,
    the finding of overlaps using more efficient means, such as:
    via an Interval tree.

    :param region:
    """
    for _, activeregion in self.actives.items():
      if region.overlaps(activeregion):
        yield (activeregion, region)

  def addoverlap(self, regionpair: RegionPair):
    """
    Add the given pair of Regions to the list of overlaps.
    This method should be overridden in subclasses to implement:
    
    - The addition of a edge in the intersection graph between the given
      region pair and labelling of the edge with additional information,
    - The addition of a branch in the interval tree for the given
      region pair and labelling of the branch with additional information.

    :param regionpair:
    """
    self.overlaps.append(regionpair)

  def oninit(self, dimension: int):
    """
    Initialize the evaluation of the RegionSet in the SweeplnRT
    with the given dimensions. This method should be overridden in
    subclasses to implement:

    - The creation of nodes in the intersection graph for each Region.
    - The creation of the interval tree root in preparation for the
      addition of branches and leaves associated with the overlaps.

    :param dimension:
    """
    assert self.binded and not self.initialized
    assert 0 <= dimension < self.regionset.dimension

    self.dimension = dimension
    self.actives   = {}
    self.overlaps  = []

  def onbegin(self, event: Event):
    """
    When a Begin Event is encountered in the SweeplnRT evaluation, this
    method is invoked with that Event. Invokes findoverlaps and 
    addoverlap methods from here. Adds the newly active Region to the
    set of active Regions.

    :param event:
    """
    region = event.context

    assert self.binded and self.initialized
    assert region.id not in self.actives

    for regionpair in self.findoverlaps(region): 
      self.addoverlap(regionpair)
    
    self.actives[region.id] = region

  def onend(self, event: Event):
    """
    When an End Event is encountered in the SweeplnRT evaluation, this
    method is invoked with that Event. Removes the ending Region from
    to the set of active Regions.

    :param event:
    """
    region_id = event.context.id

    assert self.binded and self.initialized
    assert region_id in self.actives

    del self.actives[region_id]

  def onfinalize(self) -> List[RegionPair]:
    """
    When the SweeplnRT evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this SweeplnAlg. Returns
    the result of the sweepline algorithm; for this base implementation
    returns the list of Region overlapping pairs.

    This method should be overridden in subclasses to implement any
    cleanup or finalization routines for data structures, such as
    intersection graphs and interval trees, or initialize the next
    pass on a different dimension for multiple pass versions of the
    sweepline algorithm. Should return references to the generated
    intersection graphs and interval trees.
    """
    assert self.binded and self.initialized
    assert len(self.actives) == 0

    self.dimension = None
    return self.overlaps


class SweeplnRT:
  """
  Runtime for the generalized single-pass sweepline algorithm.
  This class implements the sorting and determining the overlapping
  Regions along a specified dimension via one or more SweeplnAlg
  instances. Loops over that event generated by the RegionSet's
  timeline, calls the onbegin or onend methods of the SweeplnAlgs
  depending on EventKind.

  Properties:       regionset, evaluators
  Special Methods:  __init__
  Methods:          put, evaluate
  """
  regionset: RegionSet
  evaluators: List[SweeplnAlg]

  def __init__(self, regionset: RegionSet):
    """
    Initialize the sweepline runtime with the given RegionSet
    and an empty list of SweeplnAlgs.

    :param regionset:
    """
    self.regionset = regionset
    self.evaluators = []

  def put(self, evaluator: SweeplnAlg):
    """
    Adds the given SweeplnAlg to the list of evaluators for
    this sweepline algorithm Runtime to bind and execute
    when evaluating the input Regions.

    :param evaluator:
    """
    assert evaluator not in self.evaluators
    assert evaluator.runtime == None

    self.evaluators.append(evaluator)
    evaluator.bind(self)

  def evaluate(self, dimension: int) -> List[Any]:
    """
    Execute the sweepline algorithm on the set of Regions
    along the given dimension. Invokes the SweeplnAlg at the initialization phase,
    when encountering the beginning of an overlap and ending of an overlap Events,
    and at the finalization phase of the algorithm. Returns a list of results, one
    result for each SweeplnAlg.

    :param dimension:
    """
    assert 0 <= dimension < self.regionset.dimension
    assert len(self.evaluators) > 0

    results = []

    # Initialization
    for evaluator in self.evaluators:
      evaluator.oninit(dimension)

    # Sweep / Single-Pass
    for event in self.regionset.timeline[dimension]:
      if event.kind == EventKind.Begin:
        for evaluator in self.evaluators:
          evaluator.onbegin(event)
      elif event.kind == EventKind.End:
        for evaluator in self.evaluators:
          evaluator.onend(event)

    # Finalization
    for evaluator in self.evaluators:
      results.append(evaluator.onfinalize())

    return results
