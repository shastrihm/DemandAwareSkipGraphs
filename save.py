
from SkipGraph import SkipGraph, generate_balanced_skipgraph
from SortedLinkedList import SortedLinkedList, LLNode
import random

class SplaySkipGraph(SkipGraph):
    def __init__(self):
        SkipGraph.__init__(self)

    def tree_rotate(self, LL):
        """
        Performs a tree rotation along the edge connecting LL and its parent.

            r
            `
            P
           ` `
          `   `
          C    LL
               ` `
               `  `
               A   B

         becomes
            r
            `
            LL
           ` `
          `   `
          P    B
         ` `
        `  `
        C   A

        ((A,B,C are sub-skipgraphs))
        """
        assert(LL.parent is not None)
        A = LL.children[1]
        B = LL.children[0]
        P = LL.parent

        r = P.parent

        # left rotation
        if P.children[0] is LL:
            C = P.children[1]
            LL.children[1] = P
            P.parent = LL
            P.children[0] = A
            if A is not None:
                A.parent = P

        # right rotation
        elif P.children[1] is LL:
            C = P.children[0]
            LL.children[0] = P
            P.parent = LL
            P.children[1] = B
            if B is not None:
                B.parent = P

        # relink to parent
        if r is not None:
            if r.children[0] is P:
                r.children[0] = LL
            else:
                r.children[1] = LL
            LL.parent = r
        else:
            self.level0 = LL
            LL.parent = None

        # delete redundant LL if it exists (i.e. if P now only has one child)
        if (P.children[1] is None and P.children[0] is not None) or (P.children[0] is None and P.children[1] is not None):
            b = 1 if P.children[1] is not None else 0
            C = P.children[b]
            C.parent = LL
            bb = 1 if LL.children[1] is P else 0
            LL.children[bb] = C

    def zig(self, LL):
        self.tree_rotate(LL)

    def zig_zig(self, LL):
        """
        Equivalently, zag-zag
        """
        pbit = LL.parent.children[1] is LL
        cbit = LL.parent.parent.children[1] is LL.parent
        assert(pbit == cbit)
        self.tree_rotate(LL.parent)
        self.tree_rotate(LL)

    def zig_zag(self, LL):
        """
        equivalently, zag-zig
        """
        pbit = LL.parent.children[1] is LL
        cbit = LL.parent.parent.children[1] is LL.parent
        assert(pbit != cbit)
        self.tree_rotate(LL)
        self.tree_rotate(LL)

    def splay(self, LL, rootLL, iteration = 0):
        """
        splays LL to specified root.
        When called externally (i.e. not recursively),
        input LL will be a leaf node.
        """
        if iteration == 0:
            self.rootLLparent = rootLL.parent
        if LL.parent is self.rootLLparent:
            return
        if LL.parent.parent is self.rootLLparent:
            self.zig(LL)
            self.splay(LL, rootLL, iteration = 1)
            return
        pbit = LL.parent.children[1] is LL
        cbit = LL.parent.parent.children[1] is LL.parent
        if pbit == cbit:
            self.zig_zig(LL)
            self.splay(LL, rootLL, iteration = 1 )
            return
        else:
            self.zig_zag(LL)
            self.splay(LL, rootLL, iteration = 1)
            return


    def reverse_splay(self, LL, destLL):
        """
        reverse splays LL to specified dest LL (also a leaf node), such that at the end
        they are linked together at a length two LL
        """

    def amend(self):
        """
        -amend memvecs to reflect new skip graph structure
        -amend LL contents themselves
        -amend self.level attrs for SortedLinkedLists
        -amend LLNode.neighbors to reflect new neighbors in each new LL
        -delete redundant Linked lists to preserve internal node has 2 children proeprty
        """
        pass

S = generate_balanced_skipgraph(16, SplaySkipGraph)
S.visualize("before.png")
node = S.level0.children[0].children[0].children[0].children[0]
S.splay(node, S.level0)
S.visualize("after.png")

# S.visualize("after.png")
# S.tree_rotate(S.level0.children[0].children[0])
# S.visualize("after1.png")
# S.tree_rotate(S.level0.children[0])
# S.visualize("after2.png")
