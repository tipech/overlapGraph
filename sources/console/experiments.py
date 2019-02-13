#!/usr/bin/env python

"""
Experiments Console Command-line
Implements the console command-line for the 'experiments' command.

Methods:
- main
"""

from itertools import chain
from typing import Iterable
from sys import argv, stdout

from sources.experiments import ExperimentsOnRIGScale, ExperimentsOnRIQPerf

from .console import File, argument, command, option


@command()
@option('--logger', type=File('w'), default=stdout)
@option('--test/--full', default=True)
@argument('experiments', nargs=-1)
def ExperimentsConsole(logger = stdout, test = True, experiments = []):
  """
  Evaluate experiments that are specified by the given list of experiments,
  as exact/prefix matches or regular expressions.

  Experiments to analyze relationship between the number of Regions and the
  number of Region overlaps, as well as relationship with between Regions and
  overlaps when the density and size of Regions is changed. Experiments to
  analyze the performance of queries over Region sets and Region intersection
  graphs. Analyzes the performance of the algorithms for each query type. \f

  Args:
    logger:
      The logging output file.
    test:   
      Boolean flag for whether or not include all
      X or series values (full experiment).
      True for test mode with reduced X or series values;
      False for full experiment.
    experiments:
      The list of experiments to evaluate (including
      experiment prefixes or regular expressions).
      If None given, evaluates all experiments.
  """
  experiments = list(experiments)
  with logger as output:
    ExperimentsOnRIGScale.evaluate(experiments, output, test)
    ExperimentsOnRIQPerf.evaluate(experiments, output, test)


def _list_experiments() -> Iterable[str]:
  """
  Dynamically generate and return a list of the
  available experiment names.

  Returns:
    The list of available experiments.
  """
  experiment_classes     = [ExperimentsOnRIGScale, ExperimentsOnRIQPerf]
  is_experiment          = lambda exp, name: callable(getattr(exp, name)) and name.startswith('experiment_')
  get_experiment_methods = lambda exp: [name.replace('experiment_', '') for name in dir(exp) if is_experiment(exp, name)]
  experiments            = chain(*map(get_experiment_methods, experiment_classes))

  return experiments


@ExperimentsConsole.add_section('experiments', 'arguments')
def format_experiments(ctx, formatter):
  with formatter.section('Available Experiments'):
    formatter.write_paragraph()
    for experiment in _list_experiments():
      formatter.write_text(f'- {experiment}')
