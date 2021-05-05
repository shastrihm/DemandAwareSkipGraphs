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

def all_SGs_rooted_at(subset, C, balanced = False):
    """
    computes all skip graphs rooted at subset and puts
    them all in C
    balanced = True: computes only all balanced skip graphs rooted at subset
    """
    C[subset] = []
    if len(subset) == 1:
        C[subset] = [[subset]]
        return
    for subsubset in list(powerset(subset)):
        if balanced:
            cond = len(subsubset) == len(subset)//2
        else:
            cond = len(subsubset) <= len(subset)//2
        if len(subsubset) > 0 and cond:
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

def all_balanced_SGs_on(V):
    """
    Returns all balanced skip graphs on node set V, represented as a list of subsets
    length of V must be power of two
    """
    C = {}
    for subset in list(powerset(V)): # in order of length
        all_SGs_rooted_at(subset, C, balanced = True)
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

def adjacent_in(SG, u, v):
    """
    returns True if u is adjacent to v in SG
    """
    SL = SL_restriction(SG, u)
    for tup in SL:
        if v in tup:
            if abs(tup.index(v) - tup.index(u)) == 1:
                return True
    return False

def SL_search_cost(SL, u, v, return_value = False):
    """
    computes cost for u to search v in Skip list restriction of u, when SL is a
    tuple of tuples sorted by increasing length
    """
    if u == v:
        if return_value:
            return (0, u)
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


def SL_search_cost_zigzag(SL, u, v, return_value = False):
    """
    computes cost for u to search v in Skip list restriction of u, when SL is a
    tuple of tuples sorted by increasing length (with zigzag method)
    """
    if u == v:
        if return_value:
            return (0, u)
        return 0

    def find(tup, v):
        x = find_le(tup, v)
        y = find_ge(tup, v)
        if abs(x - v) < abs(y - v):
            return x
        return y

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

def SL_search_path(SL, u,v):
    """
    computes search path for u to search v in Skip list restriction of u, when SL is a
    tuple of tuples sorted by increasing length
    """
    path = set([u])
    if u == v:
        return path
    if u < v:
        find = find_le
    else:
        find = find_ge

    curr = u
    for tup in SL:
        next = find(tup, v)
        if curr <= next:
            for i in range(tup.index(curr), tup.index(next)):
                path.add(tup[i])
            path.add(next)
        else:
            for i in range(tup.index(next), tup.index(curr)):
                path.add(tup[i])
            path.add(curr)
        if next == v:
            return path
        curr = next
    return path

def SG_search_cost(SG, u,v, return_value = False, zigzag = False):
    """
    computes cost to search from u to v in skip graph SG
    """
    uSL = SL_restriction(SG, u)
    if not zigzag:
        return SL_search_cost(uSL, u, v, return_value)
    else:
        return SL_search_cost_zigzag(uSL, u, v, return_value)


def SG_search_path(SG, u, v):
    """
    returns the path to search from u to v in skip graph SG
    """
    uSL = SL_restriction(SG,u)
    return SL_search_path(uSL, u, v)


def epl_SG(SG,D, optimized = math.inf):
    """
    computes expected path length of SG given demand dict D
    """
    aggregate = 0
    for k in D:
        u,v = k[0], k[1]
        if D[k] > 0:
            aggregate += D[k]*SG_search_cost(SG, u, v)
        if aggregate >= optimized:
            return -1
    return aggregate


def min_epl_exhaustive_SG(D, balanced = False, ret_cost = False):
    """
    Returns the skip graph on n nodes with minimal expected path length
    given demand D

    balanced = True: searches over only balanced skip graphs (number of nodes must be pow of 2)
    """
    n = int(math.sqrt(len(D)))
    #print("generating all skip graphs...")
    if balanced:
        SGs = all_balanced_SGs_on(list(range(0,n)))
    else:
        SGs = all_SGs_on(list(range(0,n)))

    min_cost = math.inf
    best_so_far = None

    #print("starting search...")
    i = 0
    for SG in SGs:
        cost = epl_SG(SG, D, optimized = min_cost)
        if cost != -1 and cost < min_cost:
            min_cost = cost
            best_so_far = SG
        i += 1
        # if i % 10000 == 0:
        #     print(i)

    if ret_cost:
        return (min_cost, best_so_far)
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
        if D[k] > 0 and u != v:
            nodeu = pydot.Node(str(u) + ".", shape = "circle")
            nodev = pydot.Node(str(v) + ".", shape = "circle")
            edge = pydot.Edge(nodeu, nodev, label = str(D[k]))
            graph.add_node(nodeu)
            graph.add_node(nodev)
            graph.add_edge(edge)
    graph.write_png(path)
    return graph

def demand_as_matrix(D):
    s = int(len(D)**0.5)
    X = []
    for i in range(s):
        X.append([0]*s)
    for u in range(s):
        for v in range(s):
            X[u][v] = D[(u,v)]
    return X


def visualize_tupled_SG(SG, path):
    """
    SG is a tuple-ized SG sorted in increasing order
    """
    SG = list(SG)
    SG.sort(key = len)
    SG.reverse()

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

def interleaved_tupled_SG(n):
    """
    returns the interleaved skip graph on n (power of 2) nodes
    """
    base = list(range(n))
    SG = [base]

    def helper(L):
        if len(L) == 1:
            return
        if len(L) == 2:
            SG.append([L[0]])
            SG.append([L[1]])
            return
        l = [i for i in L if L.index(i) % 2 == 0]
        r = [i for i in L if L.index(i) % 2 != 0]
        SG.append(l)
        SG.append(r)
        helper(l)
        helper(r)

    helper(base)
    SG = (tuple(x) for x in SG)
    return tuple(SG)


def spine_tupled_SG(n):
    """
    returns a random spine skip graph on n nodes
    """
    base = list(range(n))
    SG = [base]
    def helper(L):
        if len(L) == 1:
            return
        if len(L) == 2:
            SG.append([L[0]])
            SG.append([L[1]])
            return
        l = random.sample(L, k = 1)
        r = list(set(L) - set(l))
        l = sorted(l)
        r = sorted(r)
        SG.append(l)
        SG.append(r)
        helper(l)
        helper(r)

    helper(base)
    SG = (tuple(x) for x in SG)
    return tuple(SG)



def path_tupled_SG(n):
    """
    returns a path skip graph on n nodes
    """
    base = list(range(n))
    SG = [base]
    def helper(L):
        if len(L) == 1:
            return
        if len(L) == 2:
            SG.append([L[0]])
            SG.append([L[1]])
            return
        l = [i for i in L if L.index(i) <= len(L)//2]
        r = list(set(L) - set(l))
        l = sorted(l)
        r = sorted(r)
        SG.append(l)
        SG.append(r)
        helper(l)
        helper(r)

    helper(base)
    SG = (tuple(x) for x in SG)
    return tuple(SG)



def random_tupled_SG(n):
    """
    returns a random Skip graph on n nodes
    """
    base = list(range(n))
    SG = [base]

    def helper(L):
        if len(L) == 1:
            return
        if len(L) == 2:
            SG.append([L[0]])
            SG.append([L[1]])
            return
        i = random.randint(1,len(L)//2)
        l = random.sample(L, k = i)
        r = list(set(L) - set(l))
        l = sorted(l)
        r = sorted(r)
        SG.append(l)
        SG.append(r)
        helper(l)
        helper(r)

    helper(base)
    SG = (tuple(x) for x in SG)
    return tuple(SG)






def partition_increment_cost(D, partition, complement):
    SG = (partition, complement, tuple(sorted(partition + complement)))
    s = 0
    for u in partition + complement:
        for v in partition + complement:
            s+= D[(u,v)]*SG_search_cost(SG, u,v)
            s+= D[(v,u)]*SG_search_cost(SG, v,u)
    return s




def min_increment_partition_heuristic(D, N):
    """
    starting with N = [0,...,n-1], finds subset S of N such that
    epl increment is minimized between S --- N -- N \ S, and does this recursively.
    Even though this is exponential time, how good does this get?
    """
    SG = [tuple(N)]

    def helper(base):
        if len(base) == 1:
            return
        P = list(powerset(base))
        min_cost = math.inf
        best_so_far = None
        for part in P:
            if len(part) <= len(base)//2 and len(part) > 0:
                comp = tuple(set(base) - set(part))
                t = partition_increment_cost(D, part, comp)
                if t < min_cost:
                    min_cost = t
                    best_so_far = [part, comp]
        SG.append(best_so_far[0])
        SG.append(best_so_far[1])
        helper(best_so_far[0])
        helper(best_so_far[1])

    helper(SG[0])
    return tuple(SG)





if __name__ == "__main__":
    pass
