import static_opt_heuristics as h
import static_optimal_search as st
import math, operator
"""
Processing demand graph/skip graphs to visualize their
properties
"""

def really_safe_normalise_in_place(d):
    factor=1.0/math.fsum(d.values())
    for k in d:
        d[k] = d[k]*factor
    key_for_max = max(d.items(), key=operator.itemgetter(1))[0]
    diff = 1.0 - math.fsum(d.values())
    d[key_for_max] += diff

def middleman_hop_frequencies(D, SG):
    """
    given a  skip graph (tupled) on n nodes,
    returns a dict f where f[k] is the number of distinct search paths
    that node k appears in, weighted by D(u,v) for demand graph D
    """
    d = D.copy()
    really_safe_normalise_in_place(d)

    nodes = st.SG_nodes(SG)
    freqs = {n : 0 for n in nodes}
    for u in nodes:
        for v in nodes:
            path = st.SG_search_path(SG, u, v)
            for x in path:
                freqs[x] += 1*d[(u,v)]
    return freqs

def grounded_middleman_hop_frequencies(D):
    """
    returns a dict f where f[k] is the number of distinct search paths
    that node k appears in for the path graph,
    weighted by D(u,v) for demand graph D
    """
    d = D.copy()

if __name__ == "__main__":
    n = 32
    N = list(range(n))
    SG= st.interleaved_tupled_SG(n)
    #for i in range(100):
    randSG = st.random_tupled_SG(n)
    D = st.g.random_demand_dict(len(N), range = 30)
    heurSG = h.greedy_matching_heuristic(D, N)
    # x = st.epl_SG(SG, D)
    # y = st.epl_SG(heurSG, D)
    # r = st.epl_SG(randSG, D)
    # print(x, y,r, x < y)

    f1 = middleman_hop_frequencies(D, heurSG)
    f2 = middleman_hop_frequencies(D, randSG)
    g = {i: f1[i] - f2[i] for i in f1}

    ### WHY INTERLEAVED PERFORM BETTER THAN HEURISTICS FOR RANDOM DEMANDS?
