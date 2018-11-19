#!/usr/env/python

#
# algorithms/sweepline.py - The Sweepline Algorithm
#
# This script implements a generalized version of a single-pass
# sweepline algorithm. Implements SweeplineAlg and SweeplineRT classes, where
# the SweeplineRT (the runtime) drives the evaluation by initializing each
# SweeplineAlgs' oninit methods, looping over the sorted Events and executing
# each SweeplineAlgs' onbegin and onend handlers, and finally, invoking each
# SweeplineAlgs' onfinalize methods. The SweeplineAlg (evaluator) is a base
# class for implementations that implement these handlers and maintain the
# necessary, associated interval state of the evaluation.
#

from typing import Any, Dict, Iterable, List, Tuple

from ..datastructs.region import Region, RegionPair
from ..datastructs.regionset import RegionSet
from ..datastructs.timeline import Event, EventKind


class SweeplineAlg:
  """
  Base class for implementing a SweeplineAlg (evaluator) that is
  binded to and evaluated when the SweeplineRT evaluates a single-pass,
  sweepline along a dimension on a set of Regions.

  Properties:           runtime, regionset, dimension, actives, overlaps
  Computed Properties:  binded, initialized
  Special Methods:      __init__
  Methods:              bind, unbind, findoverlaps, addoverlap,
                        oninit, onbegin, onend, onfinalize
  """
  runtime   : 'SweeplineRT'
  regionset : RegionSet
  dimension : int
  actives   : Dict[str, Region]
  overlaps  : List[RegionPair]

  def __init__(self):
    """Initialize this SweeplineAlg with None values."""
    self.runtime = None
    self.regionset = None
    self.dimension = None

  @property
  def binded(self) -> bool:
    """
    Determine if this SweeplineAlg is binded to a SweeplineRT.
    Return True if it is binded otherwise False.
    """
    return isinstance(self.runtime, SweeplineRT)

  @property
  def initialized(self) -> bool:
    """
    Determine if this SweeplineAlg has been initialized for evaluation.
    Return True if it is initialized otherwise False.
    """
    return isinstance(self.dimension, int)

  def bind(self, runtime: 'SweeplineRT', unbind: bool = False):
    """
    Bind or attach this SweeplineAlg to the given SweeplineRT.
    If the unbind flag is True, unbinds the previous SweeplineRT if this
    SweeplineAlg is currently binded to it.

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
    Unbind or detach this SweeplineAlg from its currently 
    atteched SweeplineRT.
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
    Add the given pair of Region to the list of overlaps.
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
    Initialize the evaluation of the RegionSet in the SweeplineRT
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
    When a Begin Event is encountered in the SweeplineRT evaluation, this
    method is invoked with that Event. Invokes findoverlaps and 
    addoverlap methods from here. Adds the newly active Region to the
    set of active Regions.

    :param event:
    """
    assert self.binded and self.initialized
    assert event.context.id not in self.actives

    region = event.context
    for regionpair in self.findoverlaps(region): 
      self.addoverlap(regionpair)
    
    self.actives[region.id] = region

  def onend(self, event: Event):
    """
    When an End Event is encountered in the SweeplineRT evaluation, this
    method is invoked with that Event. Removes the ending Region from
    to the set of active Regions.

    :param event:
    """
    assert self.binded and self.initialized
    assert event.context.id in self.actives

    del self.actives[event.context.id]

  def onfinalize(self) -> List[RegionPair]:
    """
    When the SweeplineRT evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this SweeplineAlg. Returns
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

class SweeplineRT:
  """
  Runtime for the generalized single-pass sweepline algorithm.
  This class implements the sorting and determining the overlapping
  Regions along a specified dimension via one or more SweeplineAlg
  instances. Loops over that event generated by the RegionSet's
  timeline, calls the onbegin or onend methods of the SweeplineAlgs
  depending on EventKind.

  Properties:       regionset, evaluators
  Special Methods:  __init__
  Methods:          put, evaluate
  """
  regionset: RegionSet
  evaluators: List[SweeplineAlg]

  def __init__(self, regionset: RegionSet):
    """
    Initialize the Sweepline Runtime with the given RegionSet
    and an empty list of SweeplineAlgs.

    :param regionset:
    """
    self.regionset = regionset
    self.evaluators = []

  def put(self, evaluator: SweeplineAlg):
    """
    Adds the given SweeplineAlg to the list of evaluators for
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
    along the given dimension. Invokes the SweeplineAlg at the initialization phase,
    when encountering the beginning of an overlap and ending of an overlap Events,
    and at the finalization phase of the algorithm. Returns a list of results, one
    result for each SweeplineAlg.

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
