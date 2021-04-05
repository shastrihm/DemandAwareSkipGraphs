import static_opt_heuristics as h
import static_optimal_search as st
import math, operator
import colorsys
import matplotlib.colors as colors
import matplotlib.cm as cm
import pydot
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


def grounded_middleman_hop_frequencies(D):
    """
    returns a dict f where f[k] is the number of distinct search paths
    that node k appears in for the path graph on n nodes,
    weighted by D(u,v) for demand graph D
    """
    d = D.copy()
    n = int(len(d)**0.5)
    freqs = {i : 0 for i in range(n)}
    for u in range(n):
        for v in range(n):
            path = []
            if u < v:
                # [u+1, ..., v]
                path = list(range(u+1,v+1))
            elif v < u:
                # [u-1, ..., v]
                path = list(range(v,u))
            for x in path:
                freqs[x] += 1*d[(u,v)]
    return freqs

def middleman_hop_frequencies(D, SG):
    """
    given a  skip graph (tupled) on n nodes,
    returns a dict f where f[k] is the number of distinct search paths
    that node k appears in, weighted by D(u,v) for demand graph D
    """
    d = D.copy()
    #really_safe_normalise_in_place(d)

    nodes = st.SG_nodes(SG)
    freqs = {n : 0 for n in nodes}
    for u in nodes:
        for v in nodes:
            path = st.SG_search_path(SG, u, v)
            path.remove(u)
            for x in path:
                freqs[x] += 1*d[(u,v)]
    return freqs



def colormap(val, cmap = cm.rainbow):
    """
    converts val in [0,1] to color according to cmap
    https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    r,g,b = cmap(val)[:3]
    return colors.rgb2hex((r,g,b))

def color_for_LL(LL, fmap, lmap):
    """
    LL : a tuple of skip graph nodes (as in tupled SG)
    fmap : middleman hop frequences for skip graph
    lmap : middleman hop frequencies for path graph (ground)

    returns color for the LL
    """
    fp = {k:fmap[k] for k in fmap if k in LL}
    lp = {k:lmap[k] for k in fmap if k in LL}
    val = sum(fp.values())/sum(lp.values())
    return colormap(val)


def viz_middlemancolors_tupled_SG(SG, D, path):
    """
    visualizes skip graph in prefix-tree format,
    where each LL of the prefix tree is colored based on
    the sum(values_in_LL(f, LL))/sum(values_in_LL(l, LL)) where f is
    the middleman_hop_frequencies of SG, D and l is the
    grounded_middleman_hop_frequencies of D (on the line graph)

    path = filepath to output image to e.g. "fig.png"
    """
    SG = list(SG)
    SG.sort(key = len)
    SG.reverse()

    f = middleman_hop_frequencies(D, SG)
    l = grounded_middleman_hop_frequencies(D)

    graph = pydot.Dot(rankdir = "TB", fontsize = "15")
    # SG[0] should be level 0
    covered = []
    for u in SG[0]:
        SL = st.SL_restriction(SG, u)
        curr = SL[0]
        for lev in SL[1:]:
            if len(curr) == 1:
                shape = "circle"
            else:
                shape = "box"
            node1 = pydot.Node(str(curr), shape = shape, style = "filled", fillcolor = color_for_LL(curr, f, l))
            if len(lev) == 1:
                shape = "circle"
            else:
                shape = "box"
            node2 = pydot.Node(str(lev), shape = shape, style = "filled", fillcolor = color_for_LL(lev, f, l))
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
    n = 50
    D = st.g.random_demand_dict(n, range = 30)

    randSG = st.random_tupled_SG(n)
    f = middleman_hop_frequencies(D, randSG)
    l = grounded_middleman_hop_frequencies(D)

    SG = st.interleaved_tupled_SG(n)
    s = middleman_hop_frequencies(D, SG)

    heurSG = h.greedy_matching_heuristic(D, list(range(n)))
    h = middleman_hop_frequencies(D, heurSG)

    SP = st.spine_tupled_SG(n)

    # rand = {i : f[i]/l[i] for i in f}
    # interleaved = {i : s[i]/l[i] for i in s}
    # heuristic = {i : h[i]/l[i] for i in h}

    viz_middlemancolors_tupled_SG(heurSG, D, "before.png")
    viz_middlemancolors_tupled_SG(randSG, D, "after.png")
    viz_middlemancolors_tupled_SG(SG, D, "after1.png")
    path = st.path_tupled_SG(n)
    print(st.epl_SG(randSG, D), st.epl_SG(heurSG, D), st.epl_SG(SG, D), st.epl_SG(path, D))
    # sum of freqs.values() is equal to weighted path length






    ### WHY INTERLEAVED PERFORM BETTER THAN HEURISTICS FOR RANDOM DEMANDS?
