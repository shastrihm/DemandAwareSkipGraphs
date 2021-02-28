from SkipGraph import SkipGraph
from SortedLinkedList import SortedLinkedList, LLNode
import random


class AdaptiveSkipGraphV1(SkipGraph):
    """
    Variant of skip graph that adapts to the input requests in the following strategy:
    Strategy V1:
        Given a search request for node v initiated by node u, (u,v),
        the Skip Graph moves the least recently accessed node between u and v
        to the other, resulting in them being linked in a size 2 linked list.

        This means u or v will have to change their membership vector to match
        the memvec of the other. Additionally, modification to the Skip Graph
        is localized to the "sub"-skip graph beggining only in the level in which
        the last linked list containing both u and v appears.
    """
    def __init__(self):
        SkipGraph.__init__(self)
        self.LRU = {}

    def search(self, key, fromNode = None, needLL = True, giveLL = False):
        """
        Returns the node with the associated key if found, otherwise None.
        Performs adjustment if found.

        needLL doesn't do anything. Just for inheritance and driver purposes
        giveLL = True returns (v,LL_uv), the lowest common linked list between u and v, instead of just v
        """
        if isinstance(fromNode, int):
            fromNode = self.get_node(fromNode)

        v, LL = super().search(key, fromNode, needLL = True)
        if v is None:
            return None

        u = self.level0.head if fromNode is None else fromNode

        move, stay = v, u #self.__policy(u,v)

        ### This lazier implementation is much less complicated and has
        #### the exact same desired effect, moving the two nodes together
        ### in a len 2 LL.
        self.delete(move)
        move.reset()
        move.set_memvec(stay.get_memvec())
        self.insert(move)

        if giveLL:
            return (v,LL)
        return v

    def __policy(self, u, v):
        """
        chooses which of the two nodes to move to the other node in the skip graph
        Returns (n1,n2) where n1 must move to n2, and n2 stays in place.
        In this case, the node touched least recently is moved to the other.
        """
        if v not in self.LRU:
            self.LRU[v] = 0
            tbr = (v,u)
        elif u not in self.LRU:
            self.LRU[u] = 0
            tbr = (u,v)

        elif self.LRU[u] > self.LRU[v]:
            tbr = (u,v)
        else:
            tbr = (v,u)

        for k in self.LRU:
            self.LRU[k] += 1

        self.LRU[u] = 0
        self.LRU[v] = 0

        return tbr



if __name__ == "__main__":
    S = AdaptiveSkipGraphV1()
    for i in range(10):
        S.insert(i)
