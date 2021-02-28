"""
Generator.py

Functions that generate requests based on a predetermined distribution or ruleset
"""
import random
import math


def disjoint_demand_generator(n, threshold, samples = 1000):
    """
    Returns a communication request u,v such that u and v are both less
    or are both greater than threshold, where threshold < n
    """
    requests = []
    for i in range(samples):
        u = random.randint(0,n)
        v = u
        while v == u:
            if u >= threshold:
                v = random.randint(threshold, n)
            else:
                v = random.randint(0,threshold-1)
        requests.append((u,v))
    return requests


def uniform_demand_generator(n, samples = 1000):
    """
    Returns requests sampled uniformly at random.
    n is the key set [0,...,n]
    """
    requests = []
    for i in range(samples):
        u = random.randint(0,n)
        v = random.randint(0,n)
        while v == u:
            v = random.randint(0,n)
        requests.append((u,v))
    return requests

def repeated_source_constrained_demand_generator(n, source, demand, samples = 1000):
    """
    Returns sequence of request where source node is the only one initiating
    searches for set of keys in demand
    """
    requests = []
    for i in range(samples):
        u = source
        v = random.choice(demand)
        while v == u:
            v = random.choice(demand)
        requests.append((u,v))
    return requests

def repeated_source_demand_generator(n, source, samples= 1000):
    """
    Returns sequence of requests where source node is the only one
    initiating searches
    """
    requests = []
    for i in range(samples):
        u = source
        v = random.randint(0,n)
        while v == u:
            v = random.randint(0,n)
        requests.append((u,v))
    return requests


def competing_source_demand_generator(source_pool, dest_pool, samples = 1000):
    """
    Returns a sequence of requests where nodes in source_pool are the only
    ones initiating requests for nodes in dest_pool.
    Typical usage is to check what happens when two nodes compete with each other
        for a single resource:
        source_pool = [x,y]
        dest_pool = [z]
        ...
        or for all other resources (dest_pool = all nodes except x and y)
    """
    assert(len(set(source_pool).intersection(set(dest_pool))) == 0)
    requests = []
    for i in range(samples):
        u = random.choice(source_pool)
        v = random.choice(dest_pool)
        requests.append((u,v))
    return requests


def custom_distribution_demand_generator(f, samples = 1000):
    """
    Given a dictionary that weights each possible request (node pairings),
    return a communication sequence that samples from that distribution
    """
    return random.choices(list(f.keys()), weights=f.values(), k=samples)


#### return demand graphs (as dictionaries)
def init_dict(n):
    """
    Initialize blank dictionary with request pairs as keys
    """
    D = {(u,v): 0 for u,v in [(a,b) for a in list(range(n)) for b in list(range(n))]}
    assert(len(D) == n**2)
    return D

def uniform_demand_dict(n):
    """
    Uniform distribution
    """
    D = init_dict(n)
    for k in D:
        D[k] = 1
    return D

def two_cluster_demand_dict(n, thresh1, thresh2):
    """
    nodes 0 to thresh1 have (u,v) = 1, nodes thresh2 to n have (u,v) = 1,
    all other pairs 0
    """
    assert(thresh1 != thresh2)
    D = init_dict(n)
    for k in D:
        u,v = k[0],k[1]
        if u <= thresh1 and v <= thresh1:
            D[k] = 1
        elif u >= thresh2 and v >= thresh2:
            D[k] = 1
    return D

def n_cluster_demand_dict(n, clusters):
    """
    D[(u,v)] += 1 if and only if they are in the same cluster, as determined by clusters.
    Clusters is a list of lists, where cluster[i] is a list of keys.
    A more general version of 2 cluster. Can also handle nested
    clusters (clusters within clusters) -- these nested clusters will have weight
    D[(u,v)] equal to their depth in the base cluster.
        E.g. if [[1,2,3,4], [2,3,4], [2,4]] are clusters, then, for example,
        D[(1,3)] = 1,
        D[(2,3)] = 2
        D[(2,4)] = 4
    """
    D = init_dict(n)
    for cluster in clusters:
        for u in cluster:
            for v in cluster:
                if u != v:
                    D[(u,v)] += 1
    return D



def balancedtree_demand_dict(n, multiplier = 1):
    """
    n is a power of 2.
    Let all leaves of a balanced binary tree be labeled 0 ... n - 1.
    Then returns a dict where D[(u,v)] = multiplier*(1/depth(u,v)),
    where depth(u,v) = length of path from u to LL_u,v, the least common
                        ancestor of u and v.
    """
    D = init_dict(n)
    for k in D:
        u,v = k[0], k[1]
        diff = abs(u - v)
        if diff > 0:
            md = (math.floor(math.log(diff, 2)) + 1)
            D[k] = multiplier/md
    return D
