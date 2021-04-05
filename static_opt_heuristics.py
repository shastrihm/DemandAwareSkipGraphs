import static_optimal_search as st
import networkx as nx
import random


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

if __name__ == "__main__":
    n = 16
    N = list(range(n))

    for i in range(1):
        #D = st.g.two_cluster_demand_dict(len(N), n//2 - 1, n//2)
        D = st.g.random_demand_dict(len(N))
        #SG = greedy_edge_picking_heuristic(D, N, weight_fn = comprehensive_weight)
        SGrandom = st.random_tupled_SG(n)
        SG = greedy_matching_heuristic(D, N, weight_fn = comprehensive_weight)
        alg = st.epl_SG(SG, D)
        rand = st.epl_SG(SGrandom, D)
        #optcost, opt = st.min_epl_exhaustive_SG(D, ret_cost = True) #exhaustive search
        print(alg, rand)
    S = lambda k : (2**(k-1))*(((2**k)*(k-1)) + k + 1)
    #print(2*S(lg(n//2)))
    st.visualize_demand(D, "opt_demand.png")
    #st.visualize_tupled_SG(opt, "opt_sg.png")
    st.visualize_tupled_SG(SG, "opt_sg1.png")
    st.visualize_tupled_SG(SGrandom, "opt_sg_random.png")
