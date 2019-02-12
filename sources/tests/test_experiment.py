#!/usr/bin/env python

"""
Unit tests for Base Experiment

- test_experiment_csv
- test_experiment_lineplot
- test_experiment_barchart
- test_experiment_log
"""

from typing import Tuple
from unittest import TestCase

from sources.abstract import Experiment


class TestExperiment(TestCase):

  experiment: Experiment[int, Tuple[int, float]]

  def setUp(self):
    expkw = {'series': [1, 2, 3], 'x': range(0, 10)}
    experiment = Experiment('Test Experiment', 'X', ['X', 'X^2'], **expkw)

    for x in experiment.x:
      for s in experiment.series:
        experiment.sety((x, s), (s*x, s*x*x))

    self.experiment = experiment

  def test_experiment_csv(self):
    exp = self.experiment

    for measure in exp.ynames:
      with open(f'data/test_experiment_{measure}.csv', 'w', newline='') as output:
        exp.output_csv(output, measure)

  def test_experiment_lineplot(self):
    exp = self.experiment

    for measure in exp.ynames:
      with open(f'data/test_experiment_lineplot_{measure}.png', 'wb') as output:
        exp.output_lineplot(output, measure, title=f'Test Experiment: {measure}')

  def test_experiment_barchart(self):
    exp = self.experiment

    for measure in exp.ynames:
      with open(f'data/test_experiment_barchart_{measure}.png', 'wb') as output:
        exp.output_barchart(output, measure, title=f'Test Experiment: {measure}')

  def test_experiment_log(self):
    exp = self.experiment

    for measure in exp.ynames:
      with open(f'data/test_experiment_{measure}.log', 'w') as output:
        for x in exp.x:
          for s in exp.series:
            exp.output_log(output, exp.gety((x, s)))
