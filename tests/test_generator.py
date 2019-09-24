#!/usr/bin/env python

"""
Unit tests for Interval Data Class

"""

import json, os
from dataclasses import asdict, astuple
from typing import List
from unittest import TestCase

from numpy import mean

from slig.datastructs import Interval, Region, RegionSet
from generator.random_regions import RegionGenerator



class TestInterval(TestCase):

  def test_init_generator(self):

    gen = RegionGenerator()
    self.assertEqual(gen.dimension, 2)
    gen = RegionGenerator(Interval(0,1000))
    self.assertEqual(gen.dimension, 1)
    gen = RegionGenerator(Region([0,0],[1000,1000]))
    self.assertEqual(gen.dimension, 2)

    gen = RegionGenerator(sizepc=0.5)
    self.assertEqual(gen.sizepc.dimension, 2)
    gen = RegionGenerator(dimension=1,sizepc=Interval(0,0.5))
    self.assertEqual(gen.sizepc.upper, [0.5])
    gen = RegionGenerator(sizepc=Region([0,0],[0.5,0.5]))
    self.assertEqual(gen.sizepc.upper, [0.5,0.5])


  def test_get_region(self):

    gen = RegionGenerator()
    region = gen.get_region()
    self.assertTrue(isinstance(region, Region))
    self.assertTrue(gen.bounds.encloses(region))

    
  def test_get_regionset(self):

    gen = RegionGenerator()
    regionset = gen.get_regionset(10)
    self.assertTrue(isinstance(regionset, RegionSet))
    for region in regionset:
      self.assertTrue(isinstance(region, Region))
      self.assertTrue(gen.bounds.encloses(region))


  def test_store_region_set(self):

    gen = RegionGenerator()
    gen.store_regionset(100, "test.json")

    self.assertTrue(os.path.exists("test.json"))
    with open("test.json") as file:
      regionset = json.load(file)

      self.assertTrue('bounds' in regionset)
      self.assertTrue(len(regionset['regions']) == 100)
      for r in regionset['regions']:
        region = Region.from_dict(r)
        self.assertTrue(isinstance(region, Region))
        self.assertTrue(gen.bounds.encloses(region))

