"""
playground.py
Play around with input and output of different self-adjusting skip graphs
"""

import random
import generator as g
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

def two_cluster(S, n):
    S.visualize("before.png")
    for req in g.disjoint_demand_generator(n, 1 + n//2, samples = 10000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")

def repeated_source(S, n):
    S.visualize("before.png")
    for req in g.repeated_source_demand_generator(n, 0, samples = 1000000):
        u,v = req[0], req[1]
        S.search(v,u)
    S.visualize("after.png")


n = 16
realN = n - 1
constructor = BraidedSkipGraph
#S = generate_balanced_skipgraph(n, constructor)
S = generate_spine_skipgraph(n, constructor)
#S = generate_random_skipgraph(n, constructor)

repeated_source(S, realN)
