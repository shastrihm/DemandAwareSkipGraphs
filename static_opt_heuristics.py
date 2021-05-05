import static_optimal_search as st
import networkx as nx
import random
import csv
import math, operator
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd
import numpy as np

def really_safe_normalise_in_place(d):
    factor=1.0/math.fsum(d.values())
    for k in d:
        d[k] = d[k]*factor
    key_for_max = max(d.items(), key=operator.itemgetter(1))[0]
    diff = 1.0 - math.fsum(d.values())
    d[key_for_max] += diff


def comprehensive_weight(U,V,D,N):
    """
    returns the weight for edge (U,V), where U and V represnet
    two different skip graphs. (each node in this graph is a skip graph)
    D is the demand dict.
    N is the node set [0,...,n-1]

    Computes weight based on "comprehensive" improvement
    """
    u_sum = endpoint_sum(U, V, D, N)
    v_sum = endpoint_sum(V, U, D, N)
    return u_sum + v_sum


def endpoint_sum(U, V, D, N):
    U_nodes = st.SG_nodes(U)
    V_nodes = st.SG_nodes(V)
    Ubar_nodes = set(N) - set(U_nodes)
    u_sum = 0
    for u in U_nodes:
        for up in Ubar_nodes:
            d_U, result = st.SG_search_cost(U, u, up, return_value = True)
            term = d_U + abs(result - up)
            UV = U + V + (tuple(sorted(U_nodes + V_nodes)),)
            d_UV, result = st.SG_search_cost(UV, u, up, return_value = True)
            term -= d_UV + abs(result - up)
            u_sum += term*D[(u,up)]
    return u_sum


def local_distance_weight(U,V,D,N):
    """
    same as comprehensive weight, but instead of summing over U \times Ubar pairs,
    we sum over U \times V pairs
    """
    u_sum = local_endpoint_sum(U, V, D)
    v_sum = local_endpoint_sum(V, U, D)
    return u_sum + v_sum

def local_endpoint_sum(U,V,D):
    U_nodes = st.SG_nodes(U)
    V_nodes = st.SG_nodes(V)
    u_sum = 0
    for u in U_nodes:
        for up in V_nodes:
            d_U, result = st.SG_search_cost(U, u, up, return_value = True)
            term = d_U + abs(result - up)
            UV = U + V + (tuple(sorted(U_nodes + V_nodes)),)
            d_UV, result = st.SG_search_cost(UV, u, up, return_value = True)
            term -= d_UV + abs(result - up)
            u_sum += term*D[(u,up)]
    return u_sum


def constant_distance_weight(U,V,D,N):
    """
    given skip graph U and skip graph V, only computes
    \sum_{(u,v) \in U \times V} |u - v|(D(u,v) + D(v,u))
    """
    s=0
    U_nodes = st.SG_nodes(U)
    V_nodes = st.SG_nodes(V)
    for u in U_nodes:
        for v in V_nodes:
            s += abs(u - v)*(D[(u,v)] + D[(v,u)])
    return s


def constant_weight(U,V,D,N):
    """
    sanity check. we expect heuristic with constant weights to do comparatively poorly,
    since it is returning a random skip graph
    """
    return 1




##########################################################

def init_graph(D, N, weight_fn = comprehensive_weight):
    """
    Creates a graph object given by demand dict  D and list of nodes N.
    weight_fn takes two neghboring nodes U, V, and D, N and returns an edge weight for (U,V)
    """
    assert(len(D) == len(N)**2)
    G = nx.Graph()
    for k in D:
        u,v = k[0],k[1]
        if u > v: #undirected graph, so one edge per pair
            U = ((u,),)
            V = ((v,),)
            G.add_edge(U,V , weight = weight_fn(U,V,D,N))
    return G



def collapse_edge(G, edge, D, N, weight_fn = comprehensive_weight):
    """
    Given graph G with edge, collapses the edge in G by merging
    the two endpoints. Returns
    """
    u,v = edge[0], edge[1]
    Gp = nx.contracted_nodes(G, u, v, self_loops = False)
    U_nodes = st.SG_nodes(u)
    V_nodes = st.SG_nodes(v)

    new_u = u + v + (tuple(sorted(U_nodes + V_nodes)),)
    Gp = nx.relabel_nodes(Gp, {u: new_u})
    # update edges incident to collapsed node
    for e in Gp.edges(new_u):
        Gp[e[0]][e[1]]['weight'] = weight_fn(e[0], e[1], D, N)

    return Gp


def greedy_edge_picking_heuristic(D, N, weight_fn = comprehensive_weight):
    """
    iteratively collapses the maximum weight edge in the graph, merging the two nodes,
    then recomputing edge weights.
    Final node at the end is the skip graph returned by the heuristic.
    """
    G = init_graph(D, N)
    currG = G
    # find max weight edge
    while len(currG.nodes) > 1:
        edges_by_inc_weight = sorted(currG.edges(data=True), key = lambda x : x[2]['weight'], reverse = True)
        to_collapse = (edges_by_inc_weight[0][0], edges_by_inc_weight[0][1])
        currG = collapse_edge(currG, to_collapse, D, N, weight_fn)
    # return resulting skip graph
    return list(currG.nodes)[0]


def greedy_matching_heuristic(D,N, weight_fn = comprehensive_weight):
    """
    iteratively collapses the max-weight matching in the graph,
    then recomputing edge weights.
    Final node at the end is the skip graph returned by the heuristic.
    """
    G = init_graph(D, N)
    currG = G
    # find max weight matching
    while len(currG.nodes) > 1:
        matching = nx.max_weight_matching(currG)
        for edge in matching:
            to_collapse = (edge[0], edge[1])
            currG = collapse_edge(currG, to_collapse, D, N, weight_fn)
    # return resulting skip graph
    return list(currG.nodes)[0]

def lg(n):
    i = 0
    while n > 1:
        n = n//2
        i += 1
    return i

def scaling_data(start, end, step = 1, trials_per_iter = 100):
    fname = "data.csv"
    with open(fname, "a") as csvfile:
        csvwriter = csv.writer(csvfile)
        #csvwriter.writerow(["Size","Random", "MaxEdge", "MaxMatching", "Path"])
        csvwriter.writerow(["Size","Interleaved"])
        #print("Random", "MaxEdge", "MaxMatching", "Path")
        for n in range(start, end+1, step):
            R, E, M = [],[],[]
            I = []
            interleaved = st.interleaved_tupled_SG(n)
            for t in range(trials_per_iter):
                D = st.g.random_demand_dict(n)
                really_safe_normalise_in_place(D)
                # random = st.random_tupled_SG(n)
                # path = st.path_tupled_SG(n)
                # edge_picking = greedy_edge_picking_heuristic(D, list(range(n)))
                # greedy_matching = greedy_matching_heuristic(D, list(range(n)))
                # p = 1 #st.epl_SG(path, D)
                # R.append(st.epl_SG(random, D)/p)
                # E.append(st.epl_SG(edge_picking, D)/p)
                # M.append(st.epl_SG(greedy_matching, D)/p)
                I.append(st.epl_SG(interleaved, D))
            if n % 10 == 0:
                print(n)
            #csvwriter.writerow([n, sum(R)/len(R),sum(E)/len(E),sum(M)/len(M)])
            csvwriter.writerow([n, sum(I)/len(I)])

def approx_ratio_data(n, trials = 100, optimal = True):
    """
    Returns a list L of 3 lists
    L = [A, B, C]
    A is a list of size trials, of approx ratios for matching heuristic
    B ------------------------, of approx ratios for edge picking heuristic
    C ------------------------, of approx ratios for random skip graph
    n is size of skip graph, D is input demand graph
    """
    fname = "data.csv"
    with open(fname, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Random", "CME", "CMM"])
        print("Random", "CME", "CMM")
        I = st.interleaved_tupled_SG(n)
        for t in range(trials):
            D = st.g.random_demand_dict(n)
            really_safe_normalise_in_place(D)
            if optimal:
                optcost, opt = st.min_epl_exhaustive_SG(D, ret_cost = True)
            else:
                optcost = 1
            # random = st.random_tupled_SG(n)
            # edge_picking = greedy_edge_picking_heuristic(D, list(range(n)))
            # greedy_matching = greedy_matching_heuristic(D, list(range(n)))
            #
            #
            # r = st.epl_SG(random, D)/optcost
            # e = st.epl_SG(edge_picking, D)/optcost
            # m = st.epl_SG(greedy_matching, D)/optcost
            # print(r,e,m)
            # csvwriter.writerow([r,e,m])
            i = st.epl_SG(I, D)/optcost
            csvwriter.writerow([i])

def histogram(inp_file, interleaved = None):
    data = pd.read_csv(inp_file)
    rand = data["Random"]
    maxedge = data["CME"]
    maxmatching = data["CMM"]
    bins = 15
    #plt.hist(rand, bins = bins, alpha=0.5, edgecolor = "black",label='Random',weights=np.ones(len(data)) / len(data))
    #plt.hist(maxedge, bins = bins, alpha=0.5, edgecolor = "black", label='MaxEdge', color = "orange", weights=np.ones(len(data)) / len(data))
    plt.hist(maxmatching, bins = bins, alpha=0.5, edgecolor = "black", color = "green",label='MaxMatching',weights=np.ones(len(data)) / len(data))
    if interleaved is not None:
        idata = pd.read_csv(interleaved)
        plt.hist(idata["Interleaved"], bins = bins, alpha = 0.5, edgecolor = "black", color = "red", label='Interleaved',weights=np.ones(len(idata)) / len(idata))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.gca().set_title("Histogram of Weighted Path Length for n = 80 (100 trials)")
    plt.gca().legend(["Random", "CME", "CMM", "Interleaved"])
    #plt.show()
    return data

    # for individual histograms, do
    # data.hist(column = "Random", bins = 20), plt.show()

def scaling(inp_file, with_interleaved = False):
    data = pd.read_csv(inp_file)
    if with_interleaved:
        data2 = pd.read_csv("scaling_interleaved.csv")
        data3 = pd.merge(data, data2)
        ax = data3.plot(x = "Size", y = ["Random", "CME", "CMM", "Interleaved"], marker = ".")
    else:
        ax = data.plot(x = "Size", y = ["Random", "CME", "CMM"], marker = ".")
    ax.set_ylabel("Weighted Path Length")
    ax.set_xlabel("n")
    ax.set_title("Average Weighted Path Length over Random Demand")
    #plt.show()
    return data

if __name__ == "__main__":
    #histogram("approxratio_distribution_10.csv")
    #histogram("approxratio_distribution_30.csv")
    #histogram("approxratio_distribution_50.csv")
    #histogram("approxratio_distribution_70.csv")
    #scaling("scaling.csv")

    n = 8
    N = list(range(n))
    D = st.g.single_source_demand_dict(0, n)
    print(D)
    CME = greedy_edge_picking_heuristic(D, N, weight_fn = comprehensive_weight)
    CMM = greedy_matching_heuristic(D, N, weight_fn = comprehensive_weight)
    st.visualize_tupled_SG(CME, "a1.png")
    st.visualize_tupled_SG(CMM, "a2.png")
    really_safe_normalise_in_place(D)
    print(st.epl_SG(CME, D))
    print(st.epl_SG(CMM, D))


    # n = 8
    # for n in range():
    #     N = list(range(n))
    #     #D = st.g.two_cluster_demand_dict(len(N), n//2 - 1, n//2)
    #     D = st.g.random_demand_dict(n)
    #     #SG = greedy_edge_picking_heuristic(D, N, weight_fn = comprehensive_weight)
    #     SGrandom = st.random_tupled_SG(n)
    #     SG = greedy_matching_heuristic(D, N, weight_fn = comprehensive_weight)
    #     alg = st.epl_SG(SG, D)
    #     rand = st.epl_SG(SGrandom, D)
    #
    #     optcost, opt = st.min_epl_exhaustive_SG(D, ret_cost = True) #exhaustive search
    #     SGI = st.interleaved_tupled_SG(n)
    #
    #     print(alg/rand)
    # #S = lambda k : (2**(k-1))*(((2**k)*(k-1)) + k + 1)
    # #print(2*S(lg(n//2)))
    # st.visualize_demand(D, "opt_demand.png")
    # st.visualize_tupled_SG(opt, "opt_sg.png")
    # st.visualize_tupled_SG(SG, "opt_sg1.png")
    # st.visualize_tupled_SG(SGrandom, "opt_sg_random.png")
