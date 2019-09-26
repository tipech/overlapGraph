from pprint import pprint

from generator import Randoms
from generator import RegionGenerator
from slig.datastructs import Region, RegionSet, RIGraph, Interval
from slig import SLIG

gen = RegionGenerator(dimension=1,posnrng=Randoms.gauss(),sizepc=Interval(0.2,0.5))

regionset = gen.get_regionset(200)

# regionset = RegionSet(dimension=2)
# regionset.add(Region([0, 0], [5, 5]))
# regionset.add(Region([1, 1], [5, 5]))
# regionset.add(Region([2, 2], [4, 4]))

# pprint(list(regionset))

# alternatively, to save to file do:
# gen.store_regionset(100, "test.json")


alg = SLIG(regionset)
alg.prepare()
graph = alg.sweep()

# pprint(list(graph.intersections))

# alternatively, to save to file do:
# with open("graph.json", 'w+') as graphfile:
#   graph.to_output(graphfile)

results = alg.enumerate_all()
pprint(results.to_dict())

# alternatively, to save to file do:
# with open("results.json", 'w+') as resultsfile:
#   results.to_output(resultsfile)
