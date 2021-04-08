import static_opt_heuristics as hr
import static_optimal_search as st
import math, operator
import colorsys
import matplotlib.colors as colors
import matplotlib.cm as cm
import pydot
import random
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


def epl_contribution_freqs(D, SG):
    """
    given a  skip graph (tupled) on n nodes,
    returns a dict f where f[k] is the expected path length for all paths
    that start at k or end at k.
    """
    d = D.copy()
    #really_safe_normalise_in_place(d)

    nodes = st.SG_nodes(SG)
    freqs = {n : 0 for n in nodes}
    for u in nodes:
        for v in nodes:
            cost = st.SG_search_cost(SG, u, v)*d[(u,v)]
            freqs[u] += cost
    return freqs



def colormap(val, cmap = cm.rainbow):
    """
    converts val in [0,1] to color according to cmap
    https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    r,g,b = cmap(val)[:3]
    return colors.rgb2hex((r,g,b))

def color_for_LL_fmap(LL, fmap, lmap):
    """
    LL : a tuple of skip graph nodes (as in tupled SG)
    fmap : frequences for skip graph
    lmap : frequencies for path graph (ground)

    returns color for the LL based on fmaps
    """
    fp = {k:fmap[k] for k in fmap if k in LL}
    lp = {k:lmap[k] for k in fmap if k in LL}
    val = sum(fp.values())/sum(lp.values())
    return colormap(val)

def height_for_LL(LL, fmap, lmap, constant = 1.5):
    """
    same as color_for_LL, except returns the height for the LL
    """
    fp = {k:fmap[k] for k in fmap if k in LL}
    lp = {k:lmap[k] for k in fmap if k in LL}
    if sum(lp.values()) == 0:
        return constant
    else:
        val = sum(fp.values())/sum(lp.values())
    return val*constant

def color_for_LL_node_specific(u, LL, SG, D):
    """
    u : a specific node in SG
    LL : a tuple of skip graph nodes (as in tupled SG)
    SG : the skip graph that contains LL
    D : demand graph
    returns a color for the LL based on the expected path length of of all paths
    from u to nodes in the LL
    """
    if len(LL) == 1 and u in LL:
        return "white"
    cost = 0
    linecost = 0
    for v in LL:
        cost += st.SG_search_cost(SG,u,v)*D[(u,v)]
        linecost += abs(u - v)

    if linecost == 0:
        return colormap(0)
    return colormap(cost/linecost)



def viz_colors_tupled_SG(SG, path, colorfunc = None):
    """
    visualizes skip graph in prefix-tree format,
    where each LL of the prefix tree is colored based on colorfunc.
    colorfunc is a function colorfunc(LL) where LL is a linked list,
    It outputs a color.

    path = filepath to output image to e.g. "fig.png"
    """
    SG = list(SG)
    SG.sort(key = len)
    SG.reverse()

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
            node1 = pydot.Node(str(curr), shape = shape, style = "filled", fillcolor = colorfunc(curr))
            if len(lev) == 1:
                shape = "circle"
            else:
                shape = "box"
            node2 = pydot.Node(str(lev), shape = shape, style = "filled", fillcolor = colorfunc(lev))
            edge = pydot.Edge(node1, node2, arrowhead = "None")

            if set([curr, lev]) not in covered:
                graph.add_node(node1)
                graph.add_node(node2)
                graph.add_edge(edge)
                covered.append(set([curr, lev]))
            curr = lev
    graph.write_png(path)
    return graph


def viz_middlemansize_tupled_SG(SG, D, path):
    """
    visualizes skip graph in prefix-tree format,
    where each LL of the prefix tree is sized based on
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
        shape = "circle"
        for lev in SL[1:]:
            colorc, colorl = "black", "black"
            if len(curr) != 1:
                colorc = "white"
            if len(lev) != 1:
                colorl = "white"
            node1 = pydot.Node(str(curr), shape = shape, fixedsize = "shape", height = height_for_LL(curr, f, l), width = height_for_LL(curr), fontcolor = colorc)
            node2 = pydot.Node(str(lev), shape = shape, fixedsize = "shape", height = height_for_LL(lev, f, l), width = height_for_LL(lev), fontcolor = colorl)
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
    n = 32
    D = st.g.random_demand_dict(n)

    keys = list(range(n))
    random.shuffle(keys)
    idxs = [0] + sorted(random.sample(keys, k = 3)) + [len(keys)]
    clusters = []
    for i in range(len(idxs) - 1):
        clusters.append(keys[idxs[i]:idxs[i+1]])
    print(clusters)
    D = st.g.n_cluster_demand_dict(n, clusters)

    randSG = st.random_tupled_SG(n)
    f = epl_contribution_freqs(D, randSG)
    l = epl_contribution_freqs(D, st.path_tupled_SG(n))

    SG = st.interleaved_tupled_SG(n)
    s = epl_contribution_freqs(D, SG)

    heurSG = hr.greedy_edge_picking_heuristic(D, list(range(n)))
    h = epl_contribution_freqs(D, heurSG)

    SP = st.spine_tupled_SG(n)


    # rand = {i : f[i]/l[i] for i in f}
    # interleaved = {i : s[i]/l[i] for i in s}
    # heuristic = {i : h[i]/l[i] for i in h}

    u = 15
    viz_colors_tupled_SG(heurSG, "before.png", lambda LL : color_for_LL_node_specific(u, LL, heurSG, D))
    viz_colors_tupled_SG(randSG, "after.png", lambda LL : color_for_LL_node_specific(u, LL, randSG, D))
    viz_colors_tupled_SG(SG, "after1.png", lambda LL : color_for_LL_node_specific(u, LL, SG, D))
    path = st.path_tupled_SG(n)
    print(st.epl_SG(randSG, D), st.epl_SG(heurSG, D), st.epl_SG(SG, D), st.epl_SG(path, D))
    # sum of freqs.values() is equal to weighted path length





    ### WHY INTERLEAVED PERFORM BETTER THAN HEURISTICS FOR RANDOM DEMANDS?
