#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm

This script implements a generalized version of a one-pass sweep-line
algorithm. Implements RegionSweepRn and RegionSweep classes, where
the RegionSweep drives the evaluation while the RegionSweepRn executes the
specifics details of the algorithm, by RegionSweep:

- Initializing each RegionSweepRns' oninit methods
- Looping over the sorted Events and executing each RegionSweepRns'
  onbegin and onend handlers, and
- Finally, invoking each RegionSweepRns' onfinalize methods.

RegionSweepRn is a base class for implementations that implement these
handlers and maintain the necessary, associated internal state of the
evaluation.

Classes:
- RegionSweepRn
- RegionSweep
"""

from typing import Any, Dict, Iterator, List, Tuple

from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.datasets.timeline import Event, EventKind
from sources.datastructs.shapes.region import Region, RegionPair


class RegionSweepRn:
  """
  Base class for implementing a RegionSweepRn (evaluator) that is
  binded to and evaluated when the RegionSweep evaluates a one-pass,
  sweep-line along a dimension on a set of Regions.

  Attributes:
    runtime:    The RegionSweep for which its binded.
    regionset:  The RegionSet to evaluate sweep-line over.
    dimension:  The dimension to evaluate sweep-line over.
    actives:    The active Regions during sweep-line.
    data:       The data properties.

  Properties:
    binded:
      Whether or not this RegionSweepRn is binded to a
      RegionSweep. True if it is binded otherwise False.
    initialized:
      Whether or not this RegionSweepRn has been
      initialized for evaluation. True if it is
      initialized otherwise False.

  Methods:
    Special:  __init__
    Instance: bind, unbind, findoverlaps, addoverlap,
              oninit, onbegin, onend, onfinalize
  """
  runtime   : 'RegionSweep'
  regionset : RegionSet
  dimension : int
  actives   : Dict[str, Region]
  overlaps  : List[RegionPair]

  def __init__(self):
    """
    Initialize this RegionSweepRn with the default values.
    """
    self.runtime = None
    self.regionset = None
    self.dimension = None

  ### Properties: Getters

  @property
  def binded(self) -> bool:
    """
    Determine if this RegionSweepRn is binded to a RegionSweep.

    Returns:
      True:   If it is binded.
      False:  Otherwise.
    """
    return isinstance(self.runtime, RegionSweep)

  @property
  def initialized(self) -> bool:
    """
    Determine if this RegionSweepRn has been initialized for evaluation.

    Returns:
      True:   If it is initialized.
      False:  Otherwise.
    """
    return isinstance(self.dimension, int)

  ### Methods: Binding

  def bind(self, runtime: 'RegionSweep', unbind: bool = False):
    """
    Bind or attach this RegionSweepRn to the given RegionSweep.
    If the unbind flag is True, unbinds the previous RegionSweep if this
    RegionSweepRn is currently binded to it.

    Args:
      runtime:  The RegionSweep for which its binded.
      unbind:   Boolean flag whether or not to unbind the
                previous RegionSweep if this RegionSweepRn is
                currently binded to it.
    """
    if unbind:
      self.unbind()
    else:
      assert not self.binded

    self.runtime = runtime
    self.regionset = runtime.regionset

  def unbind(self):
    """
    Unbind or detach this RegionSweepRn from
    its currently atteched RegionSweep.
    """
    if self.binded:
      self.runtime = None
      self.regionset = None

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

  ### Methods: Event Callbacks

  def oninit(self, dimension: int):
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
      dimension:
        The dimension to evaluate sweep-line over.
    """
    assert self.binded and not self.initialized
    assert 0 <= dimension < self.regionset.dimension

    self.dimension = dimension
    self.actives   = {}
    self.overlaps  = []

  def onbegin(self, event: Event):
    """
    When a Begin Event is encountered in the RegionSweep evaluation, this
    method is invoked with that Event. Invokes findoverlaps and
    addoverlap methods from here. Adds the newly active Region to the
    set of active Regions.

    Args:
      event:
        The beginning Event when encountered
        in the RegionSweep evaluation.
    """
    region = event.context

    assert self.binded and self.initialized
    assert region.id not in self.actives

    for regionpair in self.findoverlaps(region):
      self.addoverlap(regionpair)

    self.actives[region.id] = region

  def onend(self, event: Event):
    """
    When an End Event is encountered in the RegionSweep evaluation, this
    method is invoked with that Event. Removes the ending Region from
    to the set of active Regions.

    Args:
      event:
        The ending Event when encountered
        in the RegionSweep evaluation.
    """
    region_id = event.context.id

    assert self.binded and self.initialized
    assert region_id in self.actives

    del self.actives[region_id]

  def onfinalize(self) -> List[RegionPair]:
    """
    When the RegionSweep evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this RegionSweepRn. Returns
    the result of the sweep-line algorithm; for this base implementation
    returns the list of Region overlapping pairs.

    This method should be overridden in subclasses to implement any
    cleanup or finalization routines for data structures, such as
    intersection graphs and interval trees, or initialize the next
    pass on a different dimension for multiple pass versions of the
    sweep-line algorithm. Should return references to the generated
    intersection graphs and interval trees.

    Returns:
      The list of Region overlapping pairs.
    """
    assert self.binded and self.initialized
    assert len(self.actives) == 0

    self.dimension = None
    return self.overlaps


class RegionSweep:
  """
  Runtime for the generalized one-pass sweep-line algorithm.
  This class implements the sorting and determining the overlapping
  Regions along a specified dimension via one or more RegionSweepRns.
  Loops over the Events generated by the RegionSet's Timeline, calls
  the oninit, onbegin, onend and onfinalize methods of the
  RegionSweepRns for each Event for each stage of the algorithm.

  Attributes:
    regionset:  The RegionSet to evaluate sweep-line over.
    evaluators: The RegionSweepRns which are binded to
                this RegionSweep.

  Methods:
    Special:    __init__
    Instance:   put, evaluate
  """
  regionset: RegionSet
  evaluators: List[RegionSweepRn]

  def __init__(self, regionset: RegionSet):
    """
    Initialize the sweep-line runtime with the given RegionSet
    and an empty list of RegionSweepRns.

    Args:
      regionset:
        The RegionSet to evaluate sweep-line over.
    """
    self.regionset = regionset
    self.evaluators = []

  def put(self, evaluator: RegionSweepRn):
    """
    Adds the given RegionSweepRn to the list of evaluators for
    this sweep-line algorithm Runtime to bind and execute
    when evaluating the input Regions.

    Args:
      evaluator:
        The RegionSweepRn to bind to this RegionSweep.
    """
    assert evaluator not in self.evaluators
    assert evaluator.runtime == None

    self.evaluators.append(evaluator)
    evaluator.bind(self)

  def evaluate(self, dimension: int) -> List[Any]:
    """
    Execute the sweep-line algorithm on the set of Regions along the given
    dimension. Invokes the RegionSweepRn at the initialization phase, when
    encountering the beginning of an overlap and ending of an overlap Events,
    and at the finalization phase of the algorithm. Returns a list of results,
    one result for each RegionSweepRn.

    Args:
      dimension:
        The dimension to evaluate sweep-line over.

    Returns:
      A list of returned value from the binded
      RegionSweepRns to this RegionSweep.
    """
    assert 0 <= dimension < self.regionset.dimension
    assert len(self.evaluators) > 0

    results = []

    # Initialization
    for evaluator in self.evaluators:
      evaluator.oninit(dimension)

    # Sweep / One-Pass
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
