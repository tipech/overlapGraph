#!/usr/bin/env python

"""
Abstract Experiments for Regions + Region Intersection Graphs

Experiments to analyze relationship involving Regions and Region Intersection
Graphs. Provide methods common for constructing Region Sets, Graphs, and
Experiments.

Classes:
- ExperimentsOnRegions
"""

from abc import ABCMeta, abstractmethod
from inspect import stack
from io import FileIO
from numbers import Number
from re import fullmatch
from sys import stdout
from typing import Any, Callable, Dict, List, Tuple, Union

from sources.abstract.experiment import Experiment
from sources.algorithms.rigctor.nxgsweepctor import NxGraphSweepCtor
from sources.datastructs.datasets.regionset import RegionSet
from sources.datastructs.rigraphs.nxgraph import NxGraph
from sources.datastructs.shapes.region import Region


class ExperimentsOnRegions(metaclass=ABCMeta):
  """
  Abstract Class

  Experiments to analyze relationship involving Regions and Region
  intersection graphs. Provide methods common for constructing Region
  sets, graphs, and experiments.

  Args:
    xmap:
      The sets of independent variable values.
    seriesmap:
      The sets of series names.
    data:
      The controlled variables values and
      additional data properties.
    measures:
      The Y names mapped to lambdas for computing
      the Y components.
    istest:
      Boolean flag for whether or not include all
      X or series values (full experiment). True for
      test mode with reduced X or series values;
      False for full experiment.
  """
  xmap:       Dict[str, List[Number]]
  seriesmap:  Dict[str, List[Number]]
  data:       Dict[str, Any]
  measures:   Dict[str, Callable]
  istest:     bool

  def __init__(self, logger: FileIO, istest: bool = True):
    """
    Initialize the Experiments involving Regions and Region
    intersection graphs.

    Args:
      logger: The logging output file.
      istest: Boolean flag for whether or not include all
              X or series values (full experiment). True for
              test mode with reduced X or series values;
              False for full experiment.
    """
    self.istest    = istest
    self.xmap      = {}
    self.seriesmap = {}
    self.measures  = {}
    self.data = {
      'logger': logger,
      'maxbound': 1000,
      'msgprefix': '{name} {function}'
    }

  ### Methods: Helpers

  def _addtests(self, tests: List[Number]) -> List[Number]:
    """
    Determines whether or not to add the given tests to the
    X-values or series of the experiments. If istest is True,
    returns an empty list, otherwise returns the given tests.

    Args:
      tests:
        The tests to add to X-values or series.

    Returns:
      Empty list:   If istest is True.
      Tests:        Otherwise.
    """
    if self.istest:
      return []
    else:
      return tests

  ### Methods: Outputs

  def output_log(self, experiment: Experiment, message: Any = None, **data):
    """
    Logs the given message with the given experiment's logger.

    Args:
      experiment: The experiment for this logger.
      message:    The output message as log entry.
                  If None, construct message from
                  data property.
      data:       The data properties to insert within
                  the given message string.
    """
    experiment.output_log(experiment.data['logger'], message,
                          experiment.data['msgprefix'], caller=2, **data)

  ### Methods: Construction

  def construct_regions(self, experiment: Experiment, nregions: int,
                              sizepc: float, dimension: int) -> RegionSet:
    """
    Construct a random collection of Regions for the given Experiment.

    Args:
      experiment:   The experiment for this set of Regions.
      nregions:     The number of Regions in this set.
      sizepc:       The maximum size of Regions as a percent
                    of the bounding Region.
      dimension:    The dimensionality of Regions.

    Returns:
      The newly constructed, randomly generated
      collection of Regions.
    """
    bounds  = Region([0]*dimension, [experiment.data['maxbound']]*dimension)
    sizepr  = Region([0]*dimension, [sizepc]*dimension)
    regions = RegionSet.from_random(nregions, bounds=bounds, sizepc_range=sizepr)

    self.output_log(experiment, {
      'nregions': nregions,
      'sizepc': sizepc,
      'dimension': dimension
    })

    return regions

  def construct_graph(self, experiment: Experiment, nregions: int,
                            sizepc: float, dimension: int) \
                            -> Tuple[RegionSet, NxGraph]:
    """
    Construct a random collection of Regions + the associated Region
    intersection graph for the given Experiment.

    Args:
      experiment:   The experiment for this graph.
      nregions:     The number of Regions in this graph.
      sizepc:       The maximum size of Regions as a percent
                    of the bounding Region.
      dimension:    The dimensionality of Regions.

    Returns:
      The newly constructed randomly generated collection
      of Regions + its associated Region intersection graph.
    """
    regions = self.construct_regions(experiment, nregions, sizepc, dimension)
    graph   = NxGraphSweepCtor.evaluate(regions)()

    self.output_log(experiment, {
      'nregions': nregions,
      'sizepc': sizepc,
      'dimension': dimension
    })

    return (regions, graph)

  def construct_experiment(self, seriesx: Tuple[str, str] = None,
                                 name: str = None, **data):
    """
    Constructs a new Experiment with the specified series and x-values and
    the caller function's name or the given experiment name.

    Args:
      seriesx:  The specific series and x-values for
                this experiment.
      name:     The name of the experiment.
      data:     The controlled variables values and
                additional data properties.

    Returns:
      The newly constructed Experiment.
    """
    if not isinstance(name, str) or len(name) == 0:
      name = stack()[1].function

    if isinstance(seriesx, Tuple):
      sname, xname = seriesx
    else:
      assert fullmatch(r'experiment_\S+_\S+', name)
      nameparts    = name.split('_')
      sname, xname = nameparts[1], nameparts[2]

    assert sname in self.seriesmap and xname in self.xmap

    ynames = [*self.measures.keys()]
    if len(ynames) == 1:
      ynames = ynames[0]

    series, x   = self.seriesmap[sname], self.xmap[xname]
    expargs     = {'xname': xname, 'ynames': ynames, 'series': series, 'x': x}
    experiment  = Experiment(name, **{**expargs, **self.data, **data})

    self.output_log(experiment, {'name': name, **expargs})

    return experiment

  ### Methods: Experiments

  @abstractmethod
  def common_experiment(self, exp: Experiment, *args, **kwargs):
    """
    Evaluate the given experiment.

    Args:
      exp:
        The experiment to be evaluated.
      args, kwargs:
        Additional arguments.
    """
    raise NotImplementedError

  ### Class Methods: Run Experiments

  @classmethod
  def evaluate(cls, experiments: List[str] = [],
                    logger: FileIO = stdout,
                    istest: bool = True):
    """
    Evaluate the specified Experiments with whether or not the experiments
    are evaluated with full parameters: X-values or subsetted X-values for
    test mode.

    Args:
      experiments:
        The list of experiments to evaluate. If None
        given, evaluates all experiments.
      logger:
        The logging output file.
      istest:
        Boolean flag for whether or not include all
        X or series values (full experiment). True for
        test mode with reduced X or series values;
        False for full experiment.
    """
    exp = cls(logger, istest)
    if len(experiments) == 0:
      for name in dir(exp):
        if callable(getattr(exp, name)) and name.startswith('experiment_'):
          getattr(exp, name)()
    else:
      for experiment in experiments:
        method = f'experiment_{experiment}'
        if hasattr(exp, method) and callable(getattr(exp, method)):
          getattr(exp, method)()
