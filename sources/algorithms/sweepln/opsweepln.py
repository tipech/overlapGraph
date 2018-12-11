#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm

This script implements a generalized version of a one-pass sweep-line 
algorithm. Implements OpSLEvaluator and OpSweepln classes, where
the OpSweepln (the algorithm) drives the evaluation by initializing each
OpSLEvaluators' oninit methods, looping over the sorted Events and executing
each OpSLEvaluators' onbegin and onend handlers, and finally, invoking each
OpSLEvaluators' onfinalize methods. The OpSLEvaluator (evaluator) is a base
class for implementations that implement these handlers and maintain the
necessary, associated interval state of the evaluation.
"""

from typing import Any, Dict, Iterable, List, Tuple

from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.timeline import Event, EventKind
from sources.datastructs.shapes.region import Region, RegionPair


class OpSLEvaluator:
  """
  Base class for implementing a OpSLEvaluator (evaluator) that is
  binded to and evaluated when the OpSweepln evaluates a one-pass,
  sweep-line along a dimension on a set of Regions.

  Properties:           runtime, regionset, dimension, actives, overlaps
  Computed Properties:  binded, initialized
  Special Methods:      __init__
  Methods:              bind, unbind, findoverlaps, addoverlap,
                        oninit, onbegin, onend, onfinalize
  """
  runtime   : 'OpSweepln'
  regionset : RegionSet
  dimension : int
  actives   : Dict[str, Region]
  overlaps  : List[RegionPair]

  def __init__(self):
    """Initialize this OpSLEvaluator with None values."""
    self.runtime = None
    self.regionset = None
    self.dimension = None

  @property
  def binded(self) -> bool:
    """
    Determine if this OpSLEvaluator is binded to a OpSweepln.
    Return True if it is binded otherwise False.
    """
    return isinstance(self.runtime, OpSweepln)

  @property
  def initialized(self) -> bool:
    """
    Determine if this OpSLEvaluator has been initialized for evaluation.
    Return True if it is initialized otherwise False.
    """
    return isinstance(self.dimension, int)

  def bind(self, runtime: 'OpSweepln', unbind: bool = False):
    """
    Bind or attach this OpSLEvaluator to the given OpSweepln.
    If the unbind flag is True, unbinds the previous OpSweepln if this
    OpSLEvaluator is currently binded to it.

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
    Unbind or detach this OpSLEvaluator from its currently 
    atteched OpSweepln.
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
    Initialize the evaluation of the RegionSet in the OpSweepln
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
    When a Begin Event is encountered in the OpSweepln evaluation, this
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
    When an End Event is encountered in the OpSweepln evaluation, this
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
    When the OpSweepln evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this OpSLEvaluator. Returns
    the result of the sweep-line algorithm; for this base implementation
    returns the list of Region overlapping pairs.

    This method should be overridden in subclasses to implement any
    cleanup or finalization routines for data structures, such as
    intersection graphs and interval trees, or initialize the next
    pass on a different dimension for multiple pass versions of the
    sweep-line algorithm. Should return references to the generated
    intersection graphs and interval trees.
    """
    assert self.binded and self.initialized
    assert len(self.actives) == 0

    self.dimension = None
    return self.overlaps


class OpSweepln:
  """
  Runtime for the generalized one-pass sweep-line algorithm.
  This class implements the sorting and determining the overlapping
  Regions along a specified dimension via one or more OpSLEvaluators.
  Loops over that event generated by the RegionSet's Timeline, calls
  the onbegin or onend methods of the OpSLEvaluators depending on
  EventKind.

  Properties:       regionset, evaluators
  Special Methods:  __init__
  Methods:          put, evaluate
  """
  regionset: RegionSet
  evaluators: List[OpSLEvaluator]

  def __init__(self, regionset: RegionSet):
    """
    Initialize the sweep-line runtime with the given RegionSet
    and an empty list of OpSLEvaluators.

    :param regionset:
    """
    self.regionset = regionset
    self.evaluators = []

  def put(self, evaluator: OpSLEvaluator):
    """
    Adds the given OpSLEvaluator to the list of evaluators for
    this sweep-line algorithm Runtime to bind and execute
    when evaluating the input Regions.

    :param evaluator:
    """
    assert evaluator not in self.evaluators
    assert evaluator.runtime == None

    self.evaluators.append(evaluator)
    evaluator.bind(self)

  def evaluate(self, dimension: int) -> List[Any]:
    """
    Execute the sweep-line algorithm on the set of Regions
    along the given dimension. Invokes the OpSLEvaluator at the initialization phase,
    when encountering the beginning of an overlap and ending of an overlap Events,
    and at the finalization phase of the algorithm. Returns a list of results, one
    result for each OpSLEvaluator.

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
