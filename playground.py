"""
playground.py
Play around with input and output of different self-adjusting skip graphs
"""

import random
import generator as g
from matplotlib import pyplot as plt
from SkipGraph import SkipGraph
from SkipGraph import generate_spine_skipgraph, generate_balanced_skipgraph, generate_random_skipgraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
from ProbDemoteSkipGraph import ProbDemoteSkipGraph
from SplaySkipGraph import SplaySkipGraph # this one is bugged
from TreeSwapSkipGraph import TreeSwapSkipGraph
from BraidedSkipGraph import BraidedSkipGraph

def test_search(S,u,v):
    S.visualize("before.png")
    S.search(v,u)
    S.visualize("after.png")


def uniform(S, n):
    S.visualize("before.png")
    for req in g.uniform_demand_generator(n, samples = 10000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

def two_cluster(S, n, partition = None):
    if partition is None:
        partition = 1 + n//2
    S.visualize("before.png")
    for req in g.disjoint_demand_generator(n, partition, samples = 1000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

def repeated_source(S, n, source = 0):
    S.visualize("before.png")
    for req in g.repeated_source_demand_generator(n, source, samples = 10000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

def repeated_source_constrained_resources(S, n, source = 0, resources = []):
    if resources == []:
        resources = list(range(n+1))
    S.visualize("before.png")
    for req in g.repeated_source_constrained_demand_generator(n, source, resources, samples = 10000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

def competing_source_single_resource(S, n, source1 = 0, source2 = None, resource = None):
    if source2 is None:
        source2 = n
    if resource is None:
        resource = (source1 + source2)//2
    S.visualize("before.png")
    for req in g.competing_source_demand_generator([source1, source2], [resource], samples = 1000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")


def competing_source_general(S, n, sources = [], resources = []):
    assert(sources != [] and resources != [])
    S.visualize("before.png")
    for req in g.competing_source_demand_generator(sources, resources, samples = 10000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

n = 64
realN = n - 1
p = 1
constructor = lambda : BraidedSkipGraph(p = p)
#S = generate_balanced_skipgraph(n, constructor)
#S = generate_spine_skipgraph(n, constructor)
S = generate_random_skipgraph(n, constructor)

S.start_data_collection()
r = random.sample(list(range(n)), 5)
print(r)
repeated_source_constrained_resources(S, realN, source = 0, resources = r)
data = S.spit_data(mode = "search_cost")
S.stop_data_collection()
