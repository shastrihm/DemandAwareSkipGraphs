from itertools import permutations,product,combinations
import math
import random




def minimum_bisection(node_set, req_dist):
    best_bisect_cost = math.inf
    best_partition = None
    for comb in combinations(node_set, len(node_set)//2):
        other = tuple(set(node_set) - set(comb))

        bisect_cost = 0
        for node in node_set:
            if node in comb:
                for o_node in other:
                    bisect_cost += req_dist[(node, o_node)]*partition_cost(node,o_node,[comb,other])
                    bisect_cost += req_dist[(o_node, node)]*partition_cost(o_node,node,[other,comb])
        if bisect_cost < best_bisect_cost:
            best_bisect_cost = bisect_cost
            best_partition = [comb, other]

    return best_partition

def partition_cost(u,v,partition):
    if u < v:
        cmp1 = lambda i, u : i > u
        cmp2 = lambda i, v : i <= v
    else:
        cmp1 = lambda i, u : i < u
        cmp2 = lambda i, v : i >= v

    u_list, v_list = partition
    c = 0
    m = u
    for i in u_list:
        if cmp1(i,u):
            if cmp2(i,v):
                c += 1
                m = i
            else:
                break
    for j in v_list:
        if cmp1(j,m):
            if cmp2(j,v):
                c += 1
    return c

def greedy_bisect(node_set, req_dist, mapping= None):
    if mapping is None:
        mapping = {i : '' for i in node_set}
    if len(node_set) == 1:
        return node_set
    left, right = minimum_bisection(node_set, req_dist)
    for i in mapping:
        if i in left:
            mapping[i] += '0'
        elif i in right:
            mapping[i] += '1'
    greedy_bisect(left, req_dist, mapping)
    greedy_bisect(right, req_dist, mapping)
    return mapping

def permify_map(mapping):
    perm = []
    for i in mapping:
        perm.insert(i, int(mapping[i],2))
    return tuple(perm)


def longestCommonPrefix(strs):
    """
    Longest common prefix among all strings in list strs
    """
    if not strs: return ""
    for i in range(len(strs[0])):
        char = strs[0][i]
        for j in range(1,len(strs)):
            if i == len(strs[j]) or strs[j][i] != char:
                return strs[0][:i]
    return strs[0]

def get_mvec(i, perm):
    """
    This can be sped up by using anything other than strings
    """
    m = bin(perm.index(i))[2:]
    m = ('0'*(int(math.log(len(perm),2))-len(m))) + m
    return m

def cost(perm ,u,v, vecs, l_uv):
    """
    Computes cost to search from u to v
    """
    if u < v:
        comp1 = lambda x, u, v: u < x and x < v
        fn = max
        comp2 = lambda x, m, v : m < x and x <= v
        m = -math.inf
    else:
        comp1 = lambda x, u, v : u > x and x > v
        fn = min
        comp2 = lambda x, m, v : m > x and x >= v
        m = math.inf

    c = 0
    for x in perm:
        first = vecs[x][: l_uv + 1] == vecs[u][: l_uv + 1]
        second = comp1(x, u, v)
        if first and second:
            c += 1
            m = fn(m, x)
    c = 0
    for x in perm:
        first = vecs[x][: l_uv + 1] == vecs[v][: l_uv + 1]
        second = comp2(x, m, v)
        c += int(first and second)
    return c


def expected_search_time(perm, req_map):
    """
    Computes expected search time for skip graph determined by perm among all possible requests,
    where the distribution of requests is given by req_map
    """
    mvec_map = {i : get_mvec(i,perm) for i in perm}
    total = 0
    for req in req_map:
        u,v = req
        l_uv = len(longestCommonPrefix([mvec_map[u],mvec_map[v]]))
        cost_uv = cost(perm, u, v, mvec_map, l_uv)
        total += req_map[(u,v)]*cost_uv
    return total

def driver(N, req_dist):
    """
    exhaustive search for skip graph with minimal expected search time
    I.e. find the optimal bijection between {0,...,2^N - 1} and {0,1}^log(N,2)
    ​
    N is a power of 2
    req_dist is a dictionary of weights on N \times N (the set of requests)
    """
    # make sure N a power of 2 (the number of nodes)
    assert(N == 0 or (N & (N - 1)) == 0)
    # a Permutation P on N represents a skip graph: for each p_i in P, p_i is
    # the node with membership vector bin(i) where bin(i) is the binary
    # representation of i
    perms = permutations(list(range(N)))

    best_cost = math.inf
    best_graph = None
    i = 0
    for perm in perms:
        c = expected_search_time(perm, req_dist)
        if c < best_cost:
            best_cost = c
            best_graph = perm
        if i % 1000 == 0:
            pass
            #print("searched ", i, " perms")
        i+=1
    return (best_graph, best_cost)

#### Usage ####
N = 4
r = {(u,v): N - abs(u-v) for u,v in [(a,b) for a in list(range(N)) for b in list(range(N))]}
# best_graph, best_cost = driver(N, r)

r = {(u,v): random.randint(0,2) for u,v in [(a,b) for a in list(range(N)) for b in list(range(N))]}
best_graph, best_cost = driver(N, r)
node_set = list(range(0,N))
check = permify_map(greedy_bisect(tuple(node_set), r))
if check != best_graph:
    t = expected_search_time(check, r)
    if expected_search_time(check, r) != best_cost:
        print(check, t, best_graph, best_cost)

def test(N):
    for i in range(100):
        r = {(u,v): random.randint(0,10) for u,v in [(a,b) for a in list(range(N)) for b in list(range(N))]}
        best_graph, best_cost = driver(N, r)
        node_set = list(range(0,N))
        check = permify_map(greedy_bisect(tuple(node_set), r))
        if check != best_graph:
            if expected_search_time(check, r) != best_cost:
                print(check, best_graph)
        print(i)
