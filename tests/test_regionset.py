#!/usr/bin/env python

"""
Unit tests for RegionSet Data Class

- test_create_regionset
"""

from dataclasses import asdict, astuple
from functools import reduce
from typing import List, Tuple
from unittest import TestCase

from numpy import mean
from pprint import pprint

from slig.datastructs import Interval, Region


class TestRegion(TestCase):

  test_regions: List[Region]