from SkipGraph import SkipGraph, generate_balanced_skipgraph, generate_spine_skipgraph, generate_random_skipgraph
from SortedLinkedList import SortedLinkedList, LLNode, shift_neighbors
from TreeSwapSkipGraph import TreeSwapSkipGraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
import random
import generator as g


class BottomUpMergeSkipGraph(AdaptiveSkipGraphV1):
    def __init__(self, p = 1):
        AdaptiveSkipGraphV1.__init__(self)
        self.p = p # probability of merging two subtrees

    def search(self, key, fromNode = None, needLL = True):
        """
        searches for key from fromNode. Returns node with that key after adjusting.
        Say u searches for v. Let LL_uv  be the lowest common LL between u and v.
        Then once v is found, v gets moved to u in the skip graph in a length 2 LL.
        We perform the adjustments as follows.
        We merge unbalanced subtrees along the path from v's leaf LL to LL_uv,
        and likewise along the path from LL_uv to u's leaf LL. We do this probabilistically,
        according to self.p
        """
        if isinstance(fromNode, int):
            fromNode = self.get_node(fromNode)
            if fromNode is None:
                print("supplied fromNode is not in skip graph")
                return

        # without adjustment
        v, LL_uv = SkipGraph.search(self, key, fromNode = fromNode, needLL = True)
        if v is None:
            return None

        # down-adjustment
        self.adjust_along_path_to_base(v.leafLL, LL_uv, up = False)
        # this moves them closer (with AdaptiveSkipGraphV1 adjustment)
        v = super().search(key, fromNode = fromNode)
        # up-adjustment
        self.adjust_along_path_to_base(fromNode.leafLL, LL_uv, up = True)

        # need to update memvecs, since moving v to u uses memvecs
        self.update_memvecs()


    def adjust_along_path_to_base(self, leaf, base, up = False):
        """
        For every two LLs, LL1 and LL2, along the path from leafLL to base, perform a merge on
        every two sibling subtrees T1 (child of LL1 not in the path), T2 (child of LL2 not in the path)
        if size(T1) + size(T2) < size(T2sibling).

        up = True: merge from base to leaf. If false, merge from leaf to base (default)
        """
        count = 0
        start = leaf
        LLs = []
        while start is not base:
            oldstart = start
            start = start.parent
            LLs.append(start.children[oldstart.which_child() ^ 1])
        if up:
            LLs.reverse()
        for i in range(0,len(LLs),2):
            if i == len(LLs) - 1:
                break
            T2 = LLs[i]
            T1 = LLs[i+1]
            if T2 is None:
                print(leaf)
                self.visualize("debug.png")
            if T1 is None:
                print(leaf)
                self.visualize("debug.png")
            if random.uniform(0,1) < self.p and len(T1) + len(T2) < len(T2.parent.children[T2.which_child() ^ 1]):
                self.merge(T1, T2)

    def merge(self, T1, T2):
        """
        Given two subtrees T1 and T2 such that T2.parent.parent == T1.parent or vice versa,
        merges them together so T1 and T2 are siblings in the resulting skip graph
        """
        assert(T1 is not self.level0)
        base = T1.parent
        assert(T2.parent.parent is T1.parent or T2.parent is T1.parent.parent)

        if T1.parent.parent is T2.parent:
            T1, T2 = T2, T1
        # first delete T2.parent and connect T2's sibling to base

            # to properly correct the routing tables for nodes in T2's subling need to first
            # delete nodes from T2 in T2.parent
        for node in T2.as_list():
            T2.parent.delete(node.key)

        T2_sibling = T2.parent.children[T2.which_child() ^ 1]
        base.children[T1.which_child() ^ 1] = T2_sibling
        T2_sibling.parent = base
        T2_sibling.update_level(-1)

        # next make a new LL to connect T1 and T2 as siblings, so T1.parent = T2.parent = LL
            # first need to pre-emptively update levels
        T1.update_level(1)

        new_parent = SortedLinkedList(level = base.level + 1)
        new_parent.parent = base
        base.children[T1.which_child()] = new_parent
        T1.parent = new_parent
        T2.parent = new_parent
        new_parent.children[T1.which_child()] = T1
        new_parent.children[T1.which_child() ^ 1] = T2

        # insert, which takes care of relinking routing tables
        for node in T1.as_list():
            new_parent.insert(node)
        for node in T2.as_list():
            new_parent.insert(node)


if __name__ == "__main__":
    S = generate_random_skipgraph(16, constructor = BottomUpMergeSkipGraph)
    # T1 = S.level0.children[1]
    # T2 = S.level0.children[0].children[1]
    # S.visualize("before.png")
    # S.merge(T1, T2)
    # S.visualize("after.png")
    S.visualize("before.png")
    for req in g.uniform_demand_generator(15):
        u,v = req[0],req[1]
        print("hi")
        S.search(u,v)
    S.visualize("after.png")
    # S.adjust_along_path_to_base(n.leafLL, S.level0.children[0])
    # S.visualize("after1.png")
