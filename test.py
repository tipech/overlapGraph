from pprint import pprint

from generator import Randoms
from generator import RegionGenerator
from slig.datastructs import Region, RegionSet, RIGraph, Interval
from slig import SLIG

from datetime import datetime

gen = RegionGenerator(dimension=2,posnrng=Randoms.gauss(),
  sizepc=Interval(0.05,0.05))

start = datetime.now()

regionset = gen.get_regionset(100000)

regionset.calculate_bounds()

end = datetime.now()
elapsed = end-start
print("Generator: ",elapsed)
# regionset.merge(regionset2)
# print(len(regionset.regions))

# regionset = RegionSet(dimension=2)
# regionset.add(Region([0, 0], [5, 5]))
# regionset.add(Region([1, 1], [5, 5]))
# regionset.add(Region([2, 2], [4, 4]))

# pprint(list(regionset))

# alternatively, to save to file do:
# gen.store_regionset(100, "test.json")
# with open("test.json", 'w+') as file:
#   regionset.to_output(file)

start = datetime.now()

alg = SLIG(regionset)
alg.prepare()
graph = alg.sweep()


end = datetime.now()
elapsed = end-start
print("Algorithm: ",elapsed)

# pprint(list(graph.intersections))

# alternatively, to save to file do:
# with open("graph.json", 'w+') as graphfile:
#   graph.to_output(graphfile)

# results = alg.enumerate_all()
# pprint(results.to_dict())

# alternatively, to save to file do:
# with open("results.json", 'w+') as resultsfile:
#   results.to_output(resultsfile)
