import static_optimal_search as st
import networkx as nx


def init_graph(D):
    """
    Creates a graph object given the set of nodes determined by demand dict D
    """
    G = nx.Graph()
    for k in D:
        u,v = k[0],k[1]
        if u != v:
            U = ((u,),)
            V = ((v,),)
            G.add_edge(U,V , weight = compute_weight(U,V,D,N))
    return G


def compute_weight(U,V,D,N):
    """
    returns the weight for edge (U,V), where U and V represnet
    two different skip graphs. (each node in this graph is a skip graph)
    D is the demand dict.
    N is the node set [0,...,n-1]
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
            assert(result != up)
            UV = U + V + (tuple(sorted(U_nodes + V_nodes)),)
            d_UV, result = st.SG_search_cost(UV, u, up, return_value = True)
            term -= d_UV + abs(result - up)
            u_sum += term*D[(u,up)]
    return u_sum


def collapse_edge(G, edge):
    """
    Given graph G with edge, collapses the edge in G by merging
    the two endpoints
    """
    pass
    #contracted_nodes(G, )

if __name__ == "__main__":
    x = st.all_SGs_on([0,1,2,3])
    U = ((0,),)
    V = ((2,),)
    N = [0,1,2,3,4,5,6]
    D = st.g.uniform_demand_dict(7)
