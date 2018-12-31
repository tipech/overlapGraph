#!/usr/bin/env python

"""
Generalized Multi-Pass Sweep-line Algorithm

This script implements a generalized version of a multi-pass sweep-line
algorithm. Implements MSweepln, MSweepRunner (abstract), and MSweepPassTimeln
classes, extends Sweepln, SweepRunner and Timeline classes, where the MSweepln
drives the evaluation while the SweepRunners executes the specifics details of
the algorithm. MSweepRunner generates MSweepPassTimeln for the subsequent
passes for the evaluation of a multi-pass sweep-line algorithm.

MSweepln evaluates on each SweepRunner:
- Initialize: oninit
- While timeline is non-empty:
  - Initialize the next pass
  - For each Events, execute: onevent
  - Finalize and generate timeline for next pass
- Finalize: onfinal

Abstract Classes:
- MSweepRunner

Classes:
- MSweepPassTimeln
- MSweepln
"""

from typing import Any, Dict, List, Iterator, TypeVar

from sources.algorithms.sweepln.sweepln import Sweepln, SweepRunner
from sources.datastructs.datasets.timeline import Event, Timeline


T = TypeVar('T')
R = TypeVar('R')


class MSweepPassTimeln(Timeline[T]):
  """
  Implement a Timeline generated for each subsequent pass,
  in the evaluation of a multi-pass sweep-line algorithm.

  Generics:
    T:  Contextual object associated
        with each Event.

  Attributes:
    sequence:
      The list of Events in the Timeline,
      in the order for which they occur.

  Properties:
    length:
      The number of Events in the Timeline.

  Methods:
    Special:    __init__
    Instance:   put, events

  Inherited from Timeline:
    Abstract Methods:
      Instance: events
  """
  sequence: List[Event[T]]

  def __init__(self):
    """ Initialize this Timeline with an empty list of Events. """
    self.sequence = []

  ### Properties: Getters

  @property
  def length(self) -> int:
    """
    The number of Events in the Timeline.

    Returns:
      The length of the Event Timeline.
    """
    return len(self.sequence)

  ### Methods: Insertion

  def put(self, event: Event[T]):
    """
    Append the given Event to the sequence of Events,
    as last Event in Timeline.

    Args:
      event:
        The Event to append to the Timeline.
    """
    self.sequence.append(event)

  ### Methods: Iterations

  def events(self, **kwargs) -> Iterator[Event[T]]:
    """
    Returns an Iterator of sorted Events.

    Args:
      kwargs: Additional arguments.

    Returns:
      An Iterator of sorted Events.
    """
    return iter(sorted(self.sequence))


class MSweepRunner(SweepRunner[T, R]):
  """
  Abstract class for defining an object that binds and unbinds to 
  and evaluates over a timeline with a specific algorithm, when the
  multi-pass sweep-line algorithm is evaluated. Generates the subsequent
  sweep-line passes for the multi-pass sweep-line algorithm if is the
  master SweepRunner.

  Generics:
    T:  Objects type within the Timeline.
    R:  The type of Results.

  Attributes:
    nexttimeln:
      Timeline for the next pass of the MSweepln
      sweep-line algorithm.

  Properties:
    ismaster:
      Boolean flag. Whether or not this MSweepRunner
      is assigned as the master SweepRunner in MSweepln
      that generates the subsequent sweep-line passes.

  Methods:
    Instance: onsweep

  Inherited from SweepRunner:

    Attributes:
      id:       Unique identifier for this SweepRunner.
      events:   Mapping of Event kinds to callbacks.
      sweepln:  Sweepln algorithm for which its binded.
      timeline: Timeline to evaluate sweep-line over.
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
      Instance: bind, unbind, hasevent,
                onevent, oninit, onfinal

    Abstract Methods:
      Instance: results
  """
  nexttimeln: MSweepPassTimeln[T]

  @property
  def ismaster(self) -> bool:
    """
    Boolean flag. Whether or not this MSweepRunner
    is assigned as the master SweepRunner in MSweepln
    that generates the subsequent sweep-line passes.

    Returns:
      True:   If is master SweepRunner.
      False:  Otherwise.
    """
    return isinstance(self.sweepln, MSweepln) and \
           self.sweepln.master is self

  ### Methods: Event Callbacks

  def onsweep(self, **kwargs):
    """
    Initialize the runner for the next sweep/pass in the MSweepln algorithm.
    This method should be overridden in subclasses.

    Args:
      kwargs:   The additional arguments.
    """
    self.nexttimeln = MSweepPassTimeln()


class MSweepln(Sweepln[T]):
  """
  The generalized multi-pass sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Attributes:
    master:
      The MSweepRunner that generates the 
      subsequent sweep-line passes.

  Inherited from Sweepln:
    Attributes:
      runners: 
        The SweepRunners which are binded 
        to this Sweepln.
      outputs:
        The dict of results generated by each
        of the SweepRunners.
      timeline:
        First pass of the sweep-line algorithm.
        The Timeline to evaluate the algorithm over.

    Methods:
      Special:  __init__, __getitem__, __setitem__
      Instance: put, evaluate

    Overridden Methods:
      Special:  __init__
      Instance: evaluate
  """
  master: SweepRunner[T, Any]

  def __init__(self, timeline: Timeline[T], master: MSweepRunner[T, Any]):
    """
    Initialize the multi-pass sweep-line algorithm with a list of
    SweepRunner with the runner that generates the subsequent passes over
    the dataset.

    Args:
      timeline:
        First pass of the sweep-line algorithm.
      master:
        The MSweepRunner that generates the
        subsequent sweep-line passes.
    """
    assert isinstance(master, MSweepRunner)

    Sweepln.__init__(self, timeline)
    Sweepln.put(self, master)
    self.master = master

  ### Methods: Evaluation

  def evaluate(self, **kwargs) -> 'MSweepln[T]':
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Invoke the SweepRunners' methods:

    - oninit:   At the initialization phase.
    - onsweep:  At the beginning of each sweep.
    - onevent:  When each event occurs.
    - onfinal:  At the finalization phase.

    Args:
      kwargs:   The arguments to be passed to runners' 
                oninit(), onsweep(), onevent() & onfinal(),
                and timeline.events() methods.

    Returns:
      This MSweepln object.
    """
    assert len(self.runners) > 0

    self.outputs = {}

    # Initialization
    for runner in self.runners:
      runner.oninit(**kwargs)

    # First Pass
    master = self.master
    timeline = self.timeline
    npass = 0

    # Multi-Pass Sweep-line
    while npass == 0 or timeline.length > 0:
      # Prepare Sweep for each Runner
      for runner in self.runners:
        if runner is master or runner.hasevent('onsweep'):
          runner.onsweep(npass=npass, **kwargs)

      # One-Pass Sweep-line
      for event in timeline.events(**kwargs):
        for runner in self.runners:
          runner.onevent(event, npass=npass, **kwargs)

      # Next Pass
      timeline = master.nexttimeln
      npass += 1

    # Finalization
    for runner in self.runners:
      runner.onfinal(**kwargs)

    return self
