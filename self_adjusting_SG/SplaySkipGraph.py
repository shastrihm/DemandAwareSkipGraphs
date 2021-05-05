
from SkipGraph import SkipGraph, generate_balanced_skipgraph, generate_spine_skipgraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
from SortedLinkedList import SortedLinkedList, LLNode
import random
import generator as g


"""

"""

class SplaySkipGraph(SkipGraph):
    def __init__(self):
        SkipGraph.__init__(self)


    def search(self, key, fromNode):
        """
        Returns the node with key as initiated by a search from fromNode.
        Adjusts after a search, if found.
        - say u successfully searches for v. Then
        - v gets splayed to LL_u,v, the least common ancestor list
        - from there, v gets reverse-splayed to u.

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

        # restructuring
        if LL.parent is not None:
            b = 1 if LL.parent.children[1] is LL else 0 # need to keep track of this for amending, in case child changes during splaying
            r = LL.parent
        else:
            b = None

        if len(LL) > 2:
            self.splay(v.leafLL, LL)
            self.reverse_splay(v.leafLL, destLL = fromNode.leafLL)
            if b is None:
                self.amend(self.level0)
            else:
                self.amend(r.children[b])
        return v


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

        #delete redundant LL if it exists (i.e. if P now only has one child)
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
        they are linked together at a length two LL, structurally.

        Recall that the skip graph invariants (memvecs, linked list contents, etc.)
        will be fixed in a post-processing step. This splay step is just
        to achieve the proper structure.
        """
        path = self.DFS(LL, destLL)
        assert(len(destLL) == 1 and len(LL) == 1)

        if len(path) == 1:
            b = path[0]
            assert(destLL is LL.children[b])
            assert(destLL.children[0] is None and destLL.children[1] is None)

            for i in [0,1]:
                destLL.children[i] = SortedLinkedList()
                destLL.children[i].insert(LLNode("X" + str(i))) # placeholder, just to get the structure
                destLL.children[i].parent = destLL

            c0 = destLL.children[0]
            c1 = destLL.children[1]
            self.swap(destLL, c0)
            self.swap(LL, c1)
            return

        elif len(path) == 2:
            b0, b1 = path[0], path[1]
            if b0 == b1:
                child = LL.children[b0]
                self.swap(LL, child)
                self.zig(LL)
                self.reverse_splay(LL, destLL)
                return
            else:
                self.zig(LL.children[b0])
                self.reverse_splay(LL, destLL)
                return

        else:
            assert(len(path) >= 3)
            b0, b1, b2 = path[0], path[1], path[2]

            if b0 != b1:
                if b2 == b1:
                    self.zig_zag(LL.children[b0].children[b1])
                else:
                    to_be_rotated = LL.children[b0].children[b1]
                    swapwith = LL.children[b0]
                    self.swap(LL, swapwith)
                    print(b0,b1)
                    self.zig_zag(to_be_rotated)
            else:
                if b2 == b1:
                    swapwith = LL.children[b0].children[b1]
                    self.swap(LL, swapwith)
                    self.zig_zig(LL) #b/c after swap, its in the tobe rotated position
                else:
                    to_be_rotated = LL.children[b0].children[b1]
                    swapwith = LL.children[b0]
                    self.swap(LL, swapwith)
                    self.zig_zig(to_be_rotated)

            self.reverse_splay(LL, destLL)

    def amend(self, fromLL):
        """
        amends the structure of the subskipgraph rooted at fromLL so that:
        -amend memvecs and restructure to reflect new skip graph structure,
        -amend LL contents themselves
        -amend self.level attrs for SortedLinkedLists
        -amend LLNode.neighbors to reflect new neighbors in each new LL
        """
        # We do this the lazy but simple way -- get the new memvecs
        # of each node with a DFS and then just reconstruct the new subskip graph
        # according to those memvecs.
        # This is easier to implement, but is a little wasteful since the splay
        # and reverse-splay steps are mostly local modifications.
        # In a distributed system the implementation should not need this amend method,
        # as all mending ought to happen locally within each tree rotation, so the
        # algorithm would terminate after calling reverse_splay. For a simulation,
        # if it gets too slow, the culprit is probably in this step.

        new_memvec_suffixes = self.get_all_leaves_with_path(self.level0)
        # for node in new_memvec_suffixes:
        #     print(node.key, new_memvec_suffixes[node])
        # self.visualize("before.png")
        # delete the subskipgraph and replace it with an emtpy Sortedlinkedlist
        if fromLL.parent is None:
            lev = 0
        else:
            lev = fromLL.parent.level

        #self.clear_and_fix_heights_LLs(fromLL, level = lev + 1) # preserves structure
        self.clear_and_fix_heights_LLs(self.level0, level = 0)
        for node in new_memvec_suffixes:
            # node.neighbors should be overwritten with appropriate
            # links for each level when inserted into each sortedlinkedlist
            node.reset()
            suffix = new_memvec_suffixes[node]
            node.set_memvec(suffix)
            #self.insert_from(startLL, node, suffix)
            self.insert(node)
        # for node in new_memvec_suffixes:
        #     print(node.key)
        #     node.print_neighbors()
        #     print()
        # self.visualize("after.png")


#S = generate_balanced_skipgraph(16, SplaySkipGraph)

#S = generate_spine_skipgraph(10, constructor = SplaySkipGraph)
# S.visualize("before.png")
# S.search(key = 0, fromNode = 9)
# S.search(key = 2, fromNode = 0)
# S.visualize("after.png")

#S.visualize("before.png")
# for i in range(1000000):
#     S = SplaySkipGraph()
#     S.init_random(list(range(10)))
#     u,v = random.randint(0,9), random.randint(0,9)
#     print(u,v)
#     S.search(v,u)
# S.visualize("after.png")

# S.visualize("before.png")
# reqs = g.uniform_demand_generator(19, samples = 100)
# for req in reqs:
#     u,v = req[0],req[1]
#     S.search(key = v, fromNode = u)
# S.visualize("after.png")
