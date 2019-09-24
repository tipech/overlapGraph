from pprint import pprint

from generator import RegionGenerator
from slig.datastructs import Region, RegionSet, RIGraph, Interval
from slig import SLIG

gen = RegionGenerator(dimension=1,sizepc=Interval(0.2,0.5))

regionset = gen.get_regionset(200)

regionset = RegionSet(dimension=2)
regionset.add(Region([0, 0], [5, 5]))
regionset.add(Region([1, 1], [5, 5]))
regionset.add(Region([2, 2], [4, 4]))

# pprint(list(regionset))

# alternatively, to save to file do:
# gen.store_regionset(100, "test.json")


alg = SLIG(regionset)
alg.prepare()
graph = alg.sweep()

# pprint(list(graph.intersections))

# alternatively, to save to file do:
# with open("output.json", 'w+') as outfile:
#   graph.to_output(outfile)

pprint(list(alg.enumerate()))