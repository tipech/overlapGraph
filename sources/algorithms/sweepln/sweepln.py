#!/usr/env/python

"""
Generalized One-Pass Sweep-line Algorithm 

This script implements a generalized version of a one-pass sweep-line
algorithm. Implements Sweepln and SweepRunner (abstract) classes, where
the Sweepln drives the evaluation while the SweepRunners executes the
specifics details of the algorithm.

Sweepln evaluates on each SweepRunner:
- Initialize: oninit
- For each Events, execute: onevent
- Finalize: onfinal

SweepRunner is a base class for implementations that implement these
handlers and maintain the necessary, associated internal state of the
evaluation.

Classes:
- SweepRunner
- Sweepln
"""

from enum import IntEnum
from typing import Any, Dict, Generic, List, TypeVar
from uuid import uuid4

from sources.datastructs.datasets.timeline import Event, Timeline


T = TypeVar('T')
R = TypeVar('R')


class SweepRunner(Generic[T, R]): # pylint: disable=E1136
  """
  Abstract class for defining an object that binds and unbinds to 
  and evaluates over a timeline with a specific algorithm, when the
  one-pass sweep-line algorithm is evaluated.

  Generics:
    T:  Objects type within the Timeline.
    R:  The type of Results.

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
    Instance: bind, unbind,
              onevent, oninit, onfinal

  Abstract Methods:
    Instance: results
  """
  id: str
  events: Dict[IntEnum, str]
  sweepln: 'Sweepln'
  timeline: Timeline[T]
  running: bool

  def __init__(self, events: Dict[IntEnum, str], id: str = ''):
    """
    Initialize this SweepRunner with the default values.
    Defines the allowed events and corresponding event callback.

    Args:
      events:
        Mapping of event kinds to callbacks.
      id:
        The unique identifier for this Region
        Randonly generated with UUID v4, if not provided.
    """
    if len(id) == 0:
      id = str(uuid4())

    assert len(id) > 0

    self.id = id
    self.events = events
    self.sweepln = None
    self.running = False

  @property
  def binded(self) -> bool:
    """
    Determine if this SweepRunner is binded to a Sweepln.

    Returns:
      True:   If it is binded.
      False:  Otherwise.
    """
    return isinstance(self.sweepln, Sweepln)

  @property
  def initialized(self) -> bool:
    """
    Determine if this SweepRunner has been initialized for evaluation.

    Returns:
      True:   If it is initialized.
      False:  Otherwise.
    """
    return self.running

  ### Methods: Binding

  def bind(self, sweepln: 'Sweepln[T]', unbind: bool = False):
    """
    Bind or attach this SweepRunner to the given Sweepln.
    If the unbind flag is True, unbinds the previous Sweepln if this
    SweepRunner is currently binded to it.

    Args:
      runtime:  The Sweepln for which its binded.
      unbind:   Boolean flag whether or not to unbind the
                previous Sweepln if this SweepRunner is
                currently binded to it.
    """
    if unbind:
      self.unbind()
    else:
      assert not self.binded

    self.sweepln = sweepln
    self.timeline = sweepln.timeline

  def unbind(self):
    """
    Unbind or detach this SweepRunner from
    its currently atteched Sweepln.
    """
    if self.binded:
      self.sweepln = None

  ### Methods: Results

  def results(self, **kwargs) -> R:
    """
    Returns the resulting values for the runner over
    the sweep-line algorithm.

    Args:
      kwargs: Arguments for customizing or
              formatting the returned results.

    Returns:
      The resulting values.
    """
    raise NotImplementedError

  ### Methods: Event Callbacks

  def onevent(self, event: Event[T], **kwargs):
    """
    Invoke the specified event in this runner for
    the Sweepln algorithm. This method calls the specific
    method that handles this event.

    Args:
      event:  The Event object
      kwargs: The arguments to be passed to the
              specific event handler.
    """
    assert isinstance(event, Event)
    assert isinstance(event.kind, IntEnum)

    if event.kind in self.events:
      eventcb = self.events[event.kind]

    assert event.kind in self.events
    assert hasattr(self, eventcb)

    getattr(self, eventcb)(event, **kwargs)

  def oninit(self, **kwargs):
    """
    Initialize the runner for the Sweepln algorithm.
    This method should be overridden in subclasses.

    Args:
      kwargs:   The additional arguments.
    """
    self.running = True
    self.sweepln[self.id] = None

  def onfinal(self, **kwargs):
    """
    Finalize the runner for the Sweepln algorithm.
    When the Sweepln evaluation is complete, the sweep is complete,
    this method is invoked. Uninitialized this SweepRunner.
    This method should be overridden in subclasses.

    Args:
      kwargs:   The arguments to be passed to
                self.results() method.
    """
    self.running = False
    self.sweepln[self.id] = self.results(**kwargs)


class Sweepln(Generic[T]): # pylint: disable=E1136
  """
  The generalized one-pass sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Attributes:
    runners: 
      The SweepRunners which are binded 
      to this Sweepln.
    outputs:
      The dict of results generated by each
      of the SweepRunners.
    timeline:
      The Timeline to evaluate the 
      algorithm over.

  Methods:
    Special:    __init__, __getitem__, __setitem__
    Instance:   put, evaluate
  """
  runners: List[SweepRunner[T, Any]]
  outputs: Dict[str, Any]
  timeline: Timeline[T]

  def __init__(self, timeline: Timeline[T]):
    """
    Initialize the sweep-line algorithm with
    an empty list of SweepRunner.

    Args:
      timeline:
        The Timeline to evaluate the algorithm over.
    """
    self.runners = []
    self.outputs = {}
    self.timeline = timeline

  ### Methods: Results

  def __getitem__(self, id: str) -> Any:
    """
    Returns the results for the specified SweepRunner
    with the given runner ID.

    Args:
      id:   The unique identifier of the 
            specified SweepRunner.

    Returns:
      The results for the specified SweepRunner.

    Raises:
      IndexError:
        If runner ID is not associated
        with a binded SweepRunner.
    """
    if not any([r.id == id for r in self.runners]):
      raise IndexError(f'Runner ID {id} not binded.')
    else:
      return self.outputs[id]

  def __setitem__(self, id: str, results: Any):
    """
    Assigns the results for the specified SweepRunner
    with the given runner ID.

    Args:
      id:       The unique identifier of the 
                specified SweepRunner.
      results:  The resulting values to be assigned.

    Raises:
      IndexError:
        If runner ID is not associated
        with a binded SweepRunner.
    """
    if not any([r.id == id for r in self.runners]):
      raise IndexError(f'Runner ID {id} not binded.')
    else:
      self.outputs[id] = results

  ### Methods: SweepRunner

  def put(self, runner: SweepRunner[T, Any]):
    """
    Adds the given SweepRunner to the list of runners for
    this sweep-line algorithm to bind and execute when evaluating the 
    input timeline.

    Args:
      runner:
        The SweepRunner to bind to this Sweepln.
    """
    assert runner not in self.runners
    assert runner.sweepln == None

    self.runners.append(runner)
    runner.bind(self)

  ### Methods: Evaluation

  def evaluate(self, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Invoke the SweepRunners' methods:

    - oninit:     At the initialization phase.
    - onevent:    When each event occurs.
    - onfinal:    At the finalization phase.

    Args:
      kwargs: The arguments to be passed to runners' 
              oninit(), onevent() & onfinal(), 
              and timeline.events() methods.
    """
    assert len(self.runners) > 0

    self.outputs = {}

    # Initialization
    for runner in self.runners:
      runner.oninit(**kwargs)

    # Sweep / One-Pass
    for event in self.timeline.events(**kwargs):
      for runner in self.runners:
        runner.onevent(event, **kwargs)

    # Finalization
    for runner in self.runners:
      runner.onfinal(**kwargs)
