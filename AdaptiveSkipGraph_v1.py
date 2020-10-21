from SkipGraph import SkipGraph
from SortedLinkedList import SortedLinkedList
import random

class AdaptiveSkipGraphV1(SkipGraph):
    """
    Variant of skip graph that adapts to the input requests in the following strategy:
    Strategy V1:
        Given a search request for node v initiated by node u, (u,v),
        the Skip Graph moves the least recently accessed node between u and v
        to the other, resulting in them being linked in a size 2 linked list.

        This means u or v will have to change their membership vector to match
        the prefix of the other. Additionally, modification to the Skip Graph
        is localized to the "sub"-skip graph beggining only in the level in which
        the last linked list containing both u and v appears.

    """
    def __init__(self):
        SkipGraph.__init__(self)
        self.LRU = {}

    def search(self, key, fromNode = None):
        """
        Returns the node with the associated key if found, otherwise None.
        Performs adjustment if found.
        """
        v, LL = super().search(key, fromNode, needLL = True)
        if v is None:
            return None

        u = self.level0.head if fromNode is None else fromNode

        move, stay = self.__policy(u,v)

        self.__delete_from_subpath(move, LL.children[move.get_memvec_bit(LL.level)])
        self.__link_nodes(move, stay, LL)
        self.__check_redundancy(LL.children[stay.get_memvec_bit(LL.level)])

        return v

    def __policy(self, u, v):
        """
        chooses which of the two nodes to move to the other node in the skip graph
        Returns (n1,n2) where n1 must move to n2, and n2 stays in place
        """
        if v not in self.LRU:
            self.LRU[v] = 0
        if u not in self.LRU:
            self.LRU[u] = 0

        if self.LRU[u] > self.LRU[v]:
            tbr = (u,v)
        else:
            tbr = (v,u)

        for k in self.LRU:
            self.LRU[k] += 1
        self.LRU[u] = 0
        self.LRU[v] = 0

        return tbr

    def __link_nodes(self, u, v, fromLL):
        """
        Moves node u to node v in the skip graph, so they are connected
        in a length 2 linked list. Starts insertion at fromLL and continues
        along the path determined by v's memvec. Not commutative.
        """
        prevLL = fromLL
        b = v.get_memvec_bit(fromLL.level) # since 0th level corresponds to len 0 prefix of
                                              # memvec, and memvec is 0 indexed
        fromLL = fromLL.children[b]
        while fromLL is not None:
            b = v.get_memvec_bit(fromLL.level)
            fromLL.insert(u)
            u.leafLL = fromLL
            u.set_memvec_bit(i = fromLL.level, newbit = b)
            prevLL = fromLL
            fromLL = fromLL.children[b]

        # init new child LL to contain just u and v
        if len(prevLL) > 2:
            newb = v.get_memvec_bit(prevLL.level + 1)
            prevLL.children[newb] = SortedLinkedList(level = prevLL.level + 1)
            u.set_memvec_bit(i = prevLL.level + 1, newbit = newb)
            prevLL.children[newb].insert(u)
            prevLL.children[newb].insert(v)
            u.leafLL = prevLL.children[newb]
            v.leafLL = prevLL.children[newb]


    def __delete_from_subpath(self, u, fromLL):
        """
        deletes node u from every LL starting
        from (AND including) fromLL up to all children LLs it
        appears in
        """
        while fromLL is not None:
            fromLL.delete(u.key)
            if len(fromLL) == 0:
                newleaf = fromLL.parent
                if len(newleaf.children[0]) == 0:
                    newleaf.children[0] = None
                elif len(newleaf.children[1]) == 0:
                    newleaf.children[1] = None
                return
            fromLL = fromLL.children[u.get_memvec_bit(fromLL.level)]

    def __check_redundancy(self, fromLL):
        """
        checks if fromLL and its parent LL are identical, if so,
        fix the redundancy and amend the membership vectors.
        Note they are only identical if the other subtree of the parent is
        empty (None)
        """

        parentLL = fromLL.parent
        if parentLL == fromLL:
            #tree surgery
            fromLL.parent = parentLL.parent
            if parentLL.parent is not None:
                if parentLL.parent.children[0] == parentLL:
                    parentLL.parent.children[0] = fromLL
                else:
                    parentLL.parent.children[1] = fromLL
            # amend membership vectors. Level0 LL has all nodes in Skip graph.
            l = parentLL.level
            self.level0.map(lambda n : n.remove_memvec_bit(l))
            # decrement level of all LLs and LLNode neighbor dicts in subtree
            self.__height_decrementer_helper(fromLL)


    def __height_decrementer_helper(self, LL):
        """
        decrements height in all linked lists from subtree rooted at LL
        """
        if LL is None:
            return
        LL.decrement_level_by_one()
        self.__height_decrementer_helper(LL.children[0])
        self.__height_decrementer_helper(LL.children[1])


if __name__ == "__main__":
    S = AdaptiveSkipGraphV1()
    for i in range(10):
        S.insert(i)
