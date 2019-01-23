#!/usr/bin/env python

from sys import argv

from sources.experiments.regionsen import RegionSensitivityExperiment


if __name__ == "__main__":
  RegionSensitivityExperiment.run_experiments(argv[1:])
