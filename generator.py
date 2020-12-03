"""
Generator.py

Functions that generate requests based on a predetermined distribution or ruleset
"""
import random


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
    Returns requests sampled uniformly at random
    """
    requests = []
    for i in range(samples):
        u = random.randint(0,n)
        v = random.randint(0,n)
        while v == u:
            v = random.randint(0,n)
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
        v = random.choice(pool)
        requests.append((u,v))
    return requests


def custom_distribution_demand_generator(f, samples = 1000):
    """
    Given a dictionary that weights each possible request (node pairings),
    return a communication sequence that samples from that distribution
    """
    return random.choices(list(f.keys()), weights=f.values(), k=samples)
