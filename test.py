
from networkx import networkx as nx

from slig.datastructs.region import Region
from slig.datastructs.rigraph import RIGraph

region1 = Region([0, 0], [5, 5])
region2 = Region([1, 2], [3, 7])

graph = RIGraph(2)
graph.put_region(region1)
graph.put_region(region2)
graph.put_intersection(region1, region2)

for r in graph.regions: 
	print(r)

for r in graph.intersections: 
	print(r)

# graph2 = nx.Graph([('A', 'B')])
# data2 = nx.json_graph.node_link_data(graph2)
# print(data2)