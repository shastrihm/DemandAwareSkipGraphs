from SkipGraph import SkipGraph, generate_balanced_skipgraph, generate_spine_skipgraph
from SortedLinkedList import SortedLinkedList, LLNode, shift_neighbors
import random
import generator as g

class TreeSwapSkipGraph(SkipGraph):
    def __init__(self, p = 1):
        """
        p = probability of tree swap
        """
        self.p = p
        SkipGraph.__init__(self)

    def search(self, key, fromNode):
        """
        Returns the node with key as initiated by a search from fromNode.
        Adjusts after a search, if found, with probability p.
        - say u successfully searches for v. Let LL_uv be their least common ancestor.
        - Let LL_u be the subskipgraph depth two from LL_uv that contains u,
            and let LL'_u be LL_u's sibling subskipgraph
        - Let LL_v be the subskipgraph depth two from LL_uv that contains v.
        - Then the restructuring swaps LL'_u and LL_v.
        (special cases require some care, i.e. a spine graph or when u and v are already in a len 2 LL.
        in this case the only thing that is different is that we only go depth one from LL_uv)

        If not found, returns None.
        fromNode can either be of type int or of type LLNode.
        """
        if isinstance(fromNode, int):
            fromNode = self.get_node(fromNode)
            if fromNode is None:
                print("supplied fromNode is not in skip graph")
                return

        v, LL = super().search(key, fromNode, needLL = True)
        if v is None:
            return None

        u = fromNode
        # swap subskipgraphs
        if self.p >= random.uniform(0,1):
            self.adjust(u, v, LL)

        return v

    def adjust(self, u, v, LL):
        """
        LL = LL_uv
        """
        temp = LL.child_with_key(v.key)
        if temp is not None:
            LL_v = temp
            temp = LL_v.child_with_key(v.key)
            if temp is not None:
                LL_v = temp

        temp = LL.child_with_key(u.key)
        if temp is not None:
            LL_u_prime = temp
            temp = LL_u_prime.child_without_key(u.key)
            if temp is not None:
                LL_u_prime = temp

        self.tree_swap(LL_u_prime, LL_v, commonLL = LL)


    def tree_swap(self, LL1, LL2, commonLL = None):
        """
        Swap subskipgraph rooted at LL1 with subskipgraph rooted at LL2
        LL1 must not be an ancestor of LL2, and vice versa

        commonLL is the lowest common ancestor between LL1 and LL2
        """
        assert(LL1 is not self.level0 and LL2 is not self.level0)
        assert(len(list(set(LL1.as_list()) & set(LL2.as_list()))) == 0) #assert one of them is not an ancestor of the other

        # tree surgery
        b1 = LL1.which_child()
        b2 = LL2.which_child()
        LL1parent = LL1.parent
        LL2parent = LL2.parent
        LL1parent.children[b1] = LL2
        LL2parent.children[b2] = LL1
        LL1.parent = LL2parent
        LL2.parent = LL1parent

        # amend LL contents from root of uprooted trees to common LL
        # have to delete first and then insert, otherwise pointers get
        # scrambled between different LLs.
        # this also fixes the routing tables for each level less than parent levels

        # delete first
        for LL in [LL1, LL2]:
            start = LL.parent
            if LL is LL1:
                nodelist = LL2.as_list()
            else:
                nodelist = LL1.as_list()
            while start is not commonLL:
                for node in nodelist:
                    start.delete(node.key)
                start = start.parent

        #fix associated LLNode routing tables for each level greater than parent levels,
        # and update SortedLinkedList.level attributes
        base1 = LL1.parent.level
        base2 = LL2.parent.level
        LL1.update_level(base1 + 1 - LL1.level)
        LL2.update_level(base2 + 1 - LL2.level)

        # insert
        for LL in [LL1, LL2]:
            start = LL.parent
            nodelist = LL.as_list()
            while start is not commonLL:
                for node in nodelist:
                    start.insert(node)
                start = start.parent

# n = 32
# #S = generate_balanced_skipgraph(16, TreeSwapSkipGraph)
# S = generate_spine_skipgraph(n, TreeSwapSkipGraph)
# # S = TreeSwapSkipGraph()
# # S.init_random(vals = list(range(16)))
#
# def uniform(S, n):
#     S.visualize("before.png")
#     for req in g.uniform_demand_generator(n, samples = 10000):
#         u,v = req[0], req[1]
#         S.search(v,u)
#     S.visualize("after.png")
#
# def two_cluster(S, n):
#     S.visualize("before.png")
#     for req in g.disjoint_demand_generator(n, 1 + n//2, samples = 10000):
#         u,v = req[0], req[1]
#         S.search(v,u)
#     S.visualize("after.png")
#
# def repeated_source(S, n):
#     S.visualize("before.png")
#     for req in g.repeated_source_demand_generator(n, 0, samples = 10000):
#         u,v = req[0], req[1]
#         S.search(v,u)
#     S.visualize("after.png")
