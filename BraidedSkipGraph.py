from SkipGraph import SkipGraph, generate_balanced_skipgraph, generate_spine_skipgraph
from TreeSwapSkipGraph import TreeSwapSkipGraph
from SortedLinkedList import SortedLinkedList, LLNode, shift_neighbors
import random
import generator as g

class BraidedSkipGraph(TreeSwapSkipGraph):
    def __init__(self, p = 1):
        """
        p = probability of tree swap
        """
        TreeSwapSkipGraph.__init__(self, p)

    def search(self, key, fromNode):
        """
        Returns the node with key as initiated by a search from fromNode.
        Adjusts after a search, if found, with probability p.
        - The adjustment is as follows: recursively apply the restructuring
                rule from TreeSwapSkipGraph until u and v are in a len 2 LL.

        If not found, returns None.
        fromNode can either be of type int or of type LLNode.
        """
        if isinstance(fromNode, int):
            fromNode = self.get_node(fromNode)
            if fromNode is None:
                print("supplied fromNode is not in skip graph")
                return

        v, LL = SkipGraph.search(self, key, fromNode = fromNode, needLL = True, offline = False)
        if v is None:
            return None

        u = fromNode
        # swap subskipgraphs
        self.adjust(u, v, LL)

        return v

    def adjust(self, u, v, LL):
        """
        LL = LL_uv
        """
        if self.p < random.uniform(0,1): # only recurse partway if coin flip fails
            return
        if u.leafLL.parent is v.leafLL.parent:
            return
        else:
            super().adjust(u,v,LL)
            v, LL =  SkipGraph.search(self, v.key, fromNode = u, needLL = True, offline = True)
            self.adjust(u,v, LL)
