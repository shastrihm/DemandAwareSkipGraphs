from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
from SkipGraph import SkipGraph
from SortedLinkedList import SortedLinkedList, LLNode
import random


class ProbDemoteSkipGraph(AdaptiveSkipGraphV1):
    def __init__(self, p=0.5):
        AdaptiveSkipGraphV1.__init__(self)
        self.p = p

    def search(self, key, fromNode = None, needLL = True):
        """
        Returns the node with the associated key if found, otherwise None.
        Performs adjustment if found. Adjustment just moves v to u, where u searched for v,
        such that u and v are in a len 2 LL. Node w is demoted one level down and inserted
        randomly into the other subtree, where w was u's previous neighbor.

        needLL doesn't do anything. Just for inheritance and driver purposes
        """
        if len(self.level0) == 0:
            print("SG is empty")
            return
        if fromNode is None:
            fromNode = self.level0.head
        if isinstance(fromNode, int):
            fromNode = self.get_node(fromNode)
        outcast = None
        if len(fromNode.leafLL.parent) == 2:
            l = fromNode.leafLL.parent
            outcast = fromNode.get_right_ptr(l.level)
            if outcast is None:
                outcast = fromNode.get_left_ptr(l.level)

        node = super().search(key, fromNode) #this brings them closer
        base = node.leafLL.parent.parent

        if outcast is not None and random.uniform(0,1) < self.p:
            self.delete(outcast)
            oldvec = outcast.get_memvec()
            oldvec[:l.level-1] + [oldvec[l.level-1]^1]
            outcast.set_memvec(oldvec[:l.level-1] + [oldvec[l.level-1]^1])
            self.insert(outcast)

        return node

    def set_p(self, p):
        self.p = p

    def get_p(self):
        return self.p

if __name__ == "__main__":
    S = ProbDemoteSkipGraph(p = 0.5)
    for i in range(10):
        S.insert(i)
