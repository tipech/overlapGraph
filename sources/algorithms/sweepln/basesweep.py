#!/usr/env/python

"""
Abstract Sweep-line Algorithm

Defines an abstract sweep-line algorithm, Sweepline class, that iterates
over the Timeline and broadcasts Events to subscribed Observers to execute
the specific details of the algorithm. Defines the abstract SweepTaskRunner
class that performs the specific computations and generates a result using the
sweep-line algorithm.

Classes:
- Sweepline
- SweepTaskRunner
"""

from abc import ABCMeta, abstractmethod
from collections import abc
from functools import wraps
from typing import Any, Callable, Generic, Iterable, Type, TypeVar, Union

from sources.abstract import Publisher, Subscriber, Timeline


T = TypeVar('T')
R = TypeVar('R')


class Sweepline(Publisher[T], abc.Callable, metaclass=ABCMeta):
  """
  Abstract class

  Definition of a sweep-line algorithm.

  Generics:
    T:  Objects type within the Timeline.

  Extends:
    Publisher[T]
    abc.Callable

  Attributes:
    timeline:
      The Timeline to evaluate the algorithm over.
  """
  timeline: Timeline[T]

  def __init__(self, timeline: Timeline[T], *args, **kwargs):
    """
    Initialize the sweep-line algorithm.

    Args:
      timeline:
        The Timeline to evaluate the algorithm over.
      args, kwargs:
        Additional arguments.
    """
    Publisher.__init__(self, *args, **kwargs)

    self.timeline = timeline

  ### Methods: Evaluation

  @abstractmethod
  def evaluate(self, *args, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Broadcast Events to the Observers.

    Args:
      args, kwargs:
        Additional arguments.
    """
    raise NotImplementedError

  def __call__(self, *args, **kwargs):
    """
    Execute the sweep-line algorithm over the attached Timeline.
    Broadcast Events to the Observers. Alias for: self.evaluate().

    Args:
      args, kwargs:
        Arguments to be passed to evaluate().
    """
    self.evaluate(*args, **kwargs)


class SweepTaskRunner(Subscriber[T], Generic[T, R]): # pylint: disable=E1136
  """
  Abstract class

  Task Runner for a sweep-line algorithm.

  Definition of a computation generated with the sweep-line algorithm.

  Generics:
    T:  Objects type within the Events.
    R:  The return type for the resulting value.

  Extends:
    Subscriber[T]
  """

  ### Properties

  @property
  @abstractmethod
  def results(self) -> R:
    """
    The resulting value from the computation generated
    with the sweep-line algorithm.

    Returns:
      The resulting value.
    """
    raise NotImplementedError

  ### Class Methods: Evaluation

  @staticmethod
  def evaluate(cls: Type['SweepTaskRunner'],
               alg: Union[Sweepline, Type[Sweepline]],
               subscribers: Iterable[Subscriber[T]] = [],
               alg_args = [], alg_kw = {}, task_args = [], task_kw = {}) \
               -> Callable[[Any], R]:
    """
    Factory function for constructing a new sweep-line task runner
    based on the sweep-line algorithm given. 

    - Constructs a new instance of the sweep-line
      algorithm or uses the given existing instance.
    - Constructs the task runner with the given 
      concrete subclass of SweepTaskRunner.
    - Subscribes the newly constructed task runner and
      the additional subscribers to the algorithm.
    - Returns a function that wraps alg.evaluate() and
      returns the computed the output resulting value.

    Args:
      cls:
        A concrete subclass of SweepTaskRunner to
        construct a new task runner instance from.
      alg:
        The sweep-line algorithm, either instance or class:

        - Sweepline: An existing instance of the algorithm
        - Type[Sweepline]: Concrete subclass of Sweepline
          to construct an new algorithm instance from.

      subscribers:
        Other Subscribers to observe the algorithm.
      alg_args, alg_kw:
        Constructor arguments for a new instance of
        the algorithm: alg.__init__().
      task_args, task_kw:
        Constructor arguments for a new instance of
        the new task runner: cls.__init__().

    Returns:
      A function to evaluate the sweep-line algorithm
      and compute the resulting value.

      Args:
        args, kwargs:
          Arguments for alg.evaluate()

      Returns:
        The resulting value.
    """
    assert issubclass(cls, SweepTaskRunner)
    assert isinstance(alg, Sweepline) or issubclass(alg, Sweepline)
    assert all([isinstance(sub, Subscriber) for sub in subscribers])

    if issubclass(alg, Sweepline):
      alg = alg(*alg_args, **alg_kw)

    task = cls(*task_args, **task_kw)
    alg.subscribe(task)

    for subscriber in subscribers:
      alg.subscribe(subscriber)

    @wraps(alg.evaluate)
    def evaluate(*args, **kwargs) -> R:
      alg.evaluate(*args, **kwargs)
      return task.results

    return evaluate
