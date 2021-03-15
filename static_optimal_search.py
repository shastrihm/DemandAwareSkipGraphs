import itertools
import math
import random
import bisect
import generator as g
import pydot


def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect.bisect_right(a, x)
    if i:
        return a[i-1]
    print(a,x)
    raise ValueError

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a):
        return a[i]
    print(a, x)
    raise ValueError

def all_SGs_rooted_at(subset, C):
    """
    computes all skip graphs rooted at subset and puts
    them all in C
    """
    C[subset] = []
    if len(subset) == 1:
        C[subset] = [[subset]]
        return
    for subsubset in list(powerset(subset)):
        if len(subsubset) > 0 and len(subsubset) <= len(subset)//2:
        #if len(subsubset) == len(subset)//2:
            othersubsubset = tuple(sorted(tuple(set(subset) - set(subsubset))))
            for left_sgs in C[subsubset]:
                for right_sgs in C[othersubsubset]:
                    left_sgs = list(left_sgs)
                    right_sgs= list(right_sgs)
                    new = [subset] + left_sgs + right_sgs
                    C[subset].append(tuple(new))


def SG_nodes(SG):
    """
    returns nodes in SG, as tuple of ints
    """
    return max(SG, key = len)

def all_SGs_on(V):
    """
    Returns all skip graphs on node set V, represented as a list of subsets
    """
    C = {}
    for subset in list(powerset(V)): # in order of length
        all_SGs_rooted_at(subset, C)
    return C[tuple(V)]


def SL_restriction(SG,u):
    """
    returns the skip list restriction of node u in skip graph SG
    """
    SL = []
    for tup in SG:
        if u in tup:
            SL.append(tup)
    SL.sort(key = len)
    return SL

def SL_search_cost(SL, u, v, return_value = False):
    """
    computes cost for u to search v in Skip list restriction of u, when SL is a
    tuple of tuples sorted by increasing length
    """
    if u == v:
        return 0
    if u < v:
        find = find_le
    else:
        find = find_ge

    curr = u
    cost = 0
    for tup in SL:
        next = find(tup, v)
        cost += abs(tup.index(curr) - tup.index(next))
        if next == v:
            curr = next
            if return_value:
                return (cost, curr)
            return cost
        curr = next
    if return_value:
        return (cost, curr)
    return cost

def SG_search_cost(SG, u,v, return_value = False):
    """
    computes cost to search from u to v in skip graph SG
    """
    uSL = SL_restriction(SG, u)
    return SL_search_cost(uSL, u, v, return_value)

def epl_SG(SG,D):
    """
    computes expected path length of SG given demand dict D
    """
    aggregate = 0
    for k in D:
        u,v = k[0], k[1]
        if D[k] > 0:
            aggregate += D[k]*SG_search_cost(SG, u, v)
    return aggregate


def min_epl_SG(D):
    """
    Returns the skip graph on n nodes with minimal expected path length
    given demand D
    """
    n = int(math.sqrt(len(D)))
    print("generating all skip graphs...")
    SGs = all_SGs_on(list(range(0,n)))

    min_cost = math.inf
    best_so_far = None

    print("starting search...")
    i = 0
    for SG in SGs:
        cost = epl_SG(SG, D)
        if cost < min_cost:
            min_cost = cost
            best_so_far = SG
        i += 1
        if i % 10000 == 0:
            print(i)

    print(min_cost)
    return best_so_far

def powerset(iterable):
    "list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def visualize_demand(D, path):
    """
    Given demand dict D and SG in nested tuple form (sorted in order
    of decreasing length),
    visualize them as png
    """
    graph = pydot.Dot(fontsize = "15")
    for k in D:
        u,v = k[0], k[1]
        if D[k] > 0 and abs(u-v) > 1:
            nodeu = pydot.Node(str(u) + ".", shape = "circle")
            nodev = pydot.Node(str(v) + ".", shape = "circle")
            edge = pydot.Edge(nodeu, nodev, label = str(D[k]))
            graph.add_node(nodeu)
            graph.add_node(nodev)
            graph.add_edge(edge)
    graph.write_png(path)
    return graph

def visualize_tupled_SG(SG, path):
    """
    SG is a tuple-ized SG sorted in increasing order
    """
    graph = pydot.Dot(rankdir = "TB", fontsize = "15")
    # SG[0] should be level 0
    covered = []
    for u in SG[0]:
        SL = SL_restriction(SG, u)
        curr = SL[0]
        for lev in SL[1:]:
            if len(curr) == 1:
                shape = "circle"
            else:
                shape = "box"
            node1 = pydot.Node(str(curr), shape = shape)
            if len(lev) == 1:
                shape = "circle"
            else:
                shape = "box"
            node2 = pydot.Node(str(lev), shape = shape)
            edge = pydot.Edge(node1, node2, arrowhead = "None")

            if set([curr, lev]) not in covered:
                graph.add_node(node1)
                graph.add_node(node2)
                graph.add_edge(edge)

                covered.append(set([curr, lev]))
            curr = lev
    graph.write_png(path)
    return graph









if __name__ == "__main__":
    n = 6
    D = g.random_demand_dict(n)
    visualize_demand(D, "opt_demand.png")
    sg = min_epl_SG(D)
    visualize_tupled_SG(sg, "opt_sg.png")
