"""
playground.py
Play around with input and output of different self-adjusting skip graphs
"""

import random
import math
from math import sqrt
import operator
import generator as g
from matplotlib import pyplot as plt
from SkipGraph import SkipGraph
from SkipGraph import generate_spine_skipgraph, generate_balanced_skipgraph, generate_random_skipgraph, generate_identical_random_skipgraphs
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
from ProbDemoteSkipGraph import ProbDemoteSkipGraph
from SplaySkipGraph import SplaySkipGraph # this one is bugged
from TreeSwapSkipGraph import TreeSwapSkipGraph
from BraidedSkipGraph import BraidedSkipGraph

def test_search(S,u,v):
    S.visualize("before.png")
    S.search(v,u)
    S.visualize("after.png")


def really_safe_normalise_in_place(d):
    factor=1.0/math.fsum(d.values())
    for k in d:
        d[k] = d[k]*factor
    key_for_max = max(d.items(), key=operator.itemgetter(1))[0]
    diff = 1.0 - math.fsum(d.values())
    d[key_for_max] += diff


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


def epl_distribution(D, n, samples = 1000):
    """
    Given demand dict D, estimates the distribution of expected
    path length of skip graphs on n nodes by random sampling
    """
    demand = g.custom_distribution_demand_generator(D, samples = samples)
    data = []
    for i in range(samples):
        S = generate_random_skipgraph(n)
        data.append(S.expected_path_length(D))
        if i % 10 == 0:
            print(str(i) + " done")
    return data
    #plt.hist(data)
    #plt.show()

def epl_best(D, n, samples = 1000):
    """
    Given demand dict D, returns the skip graph on n nodes
    with minimum expected path length found
    over 1000 random samples
    """
    demand = g.custom_distribution_demand_generator(D, samples = samples)
    data = []
    m = math.inf
    best = None
    for i in range(samples):
        S = generate_random_skipgraph(n)
        epl = S.expected_path_length(D)
        if epl < m:
            best = S
        if i % 10 == 0:
            print(str(i) + " done")
    return S





def epl_EXPERIMENT(S, D, samples = 1000, visualize = True):
    """
    Plots expected path length of S_t vs. t
    requests samples from distribution D.
    visualize = True means "before.png" and "after.png" will show
            skip graphs before and after serving all requests, respectively
    """
    if visualize:
        S.visualize("before.png")
    data = [S.expected_path_length(D)]
    demand = g.custom_distribution_demand_generator(D, samples = samples)
    samps = 0
    print("starting...")
    for req in demand:
        u,v = req[0], req[1]
        S.search(v,u)
        samps += 1
        data.append(S.expected_path_length(D))
        if samps % 100 == 0:
            print(str(samps) + " done")
    if visualize:
        S.visualize("after.png")
    return data



n = 64
realN = n - 1
p = 1

#################################################
#################################################
#################   CONSTRUCTORS    ############
#################################################
#################################################
braided = lambda : BraidedSkipGraph(p = p)
naive = lambda : ProbDemoteSkipGraph(p = 0)
treeswap = lambda : TreeSwapSkipGraph(p = p)
constructor_list = [braided, naive, treeswap]
constructor = braided


#################################################
#################################################
##### Starting skip graph initialization #########
#################################################
#################################################

#S = generate_balanced_skipgraph(n, constructor)
#S = generate_spine_skipgraph(n, constructor)
S = generate_random_skipgraph(n, constructor)
seed = random.randint(0,10000000000)
SGs = generate_identical_random_skipgraphs(n,seed,constructor_list)

#################################################
#################################################
############# Demand graph initialization #######
#################################################
#################################################

balancedtree_D = g.balancedtree_demand_dict(n, multiplier = 1)

# sqrt(n) clusters of size sqrt(n)
sqrtncluster_D = g.n_cluster_demand_dict(n, [list(range(int(i*sqrt(n)), int((i+1)*sqrt(n)))) for i in range(int(sqrt(n)))])

twocluster_D = g.two_cluster_demand_dict(n, thresh1 = 15, thresh2 = 16)
uniform_D = g.uniform_demand_dict(n)

#D = g.n_cluster_demand_dict(n, [[0,1,2,3,4,5,6,7],[0,1,2,3]])


#################################################
#################################################
################ EXPERIMENTS #################
#################################################
#################################################

def compare_all(SGs, D):
    data_array = []
    for S in SGs:
        data_array.append(epl_EXPERIMENT(S, D, samples = 1000, visualize = True))
    i = 0
    for data in data_array:
        if i == 0:
            label = "braided"
        elif i == 1:
            label = "naive"
        elif i == 2:
            label = "treeswap"
        plt.plot(data, label = label)
        i += 1
    plt.legend(loc = "upper left")

#data = epl_EXPERIMENT(S, D, samples = 1000, visualize = True)
compare_all(SGs, D)
#plt.show()



# ToDo:
# think about accounting for within linked list routing
# cliques within cliques (within each cluster, nodes form a stronger cluster)
# scaling? maybe if n = 2^(2k) is number of nodes, then break into sqrt(n) number of clusters and then
# plot? Maybe the scaling makes it so the noise associated with within-linked list routing is less prevalent,
# meaning a more meaningful picture of the cost associated with the tree-distance
