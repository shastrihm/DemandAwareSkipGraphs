from SortedLinkedList import LLNode, SortedLinkedList
import random
import os
import itertools
import pydot
import math

class SkipGraph:
    def __init__(self):
        self.level0 = SortedLinkedList(level = 0)

    def search(self, key, fromNode = None, needLL = False):
        """
        returns node with key. Otherwise returns None
        fromNode: node to start search from. Must be a node that
                    belongs in the Skip Graph.
        neadLL : also returns the specific Linked List search path ends in if True,
                 otherwise just returns the node with the key
        """
        if fromNode is None:
            fromNode = self.level0.head
            if fromNode is None:
                return None

        fromLL = fromNode.leafLL

        while fromLL is not None:
            fromNode = fromLL.search(key, fromNode)
            if fromNode.key == key:
                return fromNode if not needLL else (fromNode, fromLL)
            fromLL = fromLL.parent

        return None if not needLL else (None, None)

    def insert(self, key):
        """
        Inserts key into skip graph. Key can also be of type node.
        If key was already in the skip graph, does nothing and returns False
        """
        if isinstance(key, int):
            newNode = LLNode(key)
            if key in self.level0:
                return False
        else:
            newNode = key

        currList = self.level0
        prevList = None
        i = 0
        while currList is not None:
            currList.insert(newNode)
            prevList = currList
            nb = newNode.get_memvec_bit(i)
            currList = currList.children[nb]
            i += 1

        if len(prevList) == 1:
            newNode.leafLL = prevList
        else:
            assert(len(prevList) == 2)
            if prevList.head == newNode:
                otherNode = prevList.head.get_right_ptr(i - 1)
            else:
                otherNode = prevList.head

            ob = otherNode.get_memvec_bit(i-1)
            nb = ob ^ 1

            newNode.set_memvec_bit(i-1, nb)
            prevList.children[nb] = SortedLinkedList(level = i)
            prevList.children[nb].insert(newNode)
            prevList.children[nb].parent = prevList
            newNode.leafLL = prevList.children[nb]


            prevList.children[ob] = SortedLinkedList(level = i)
            prevList.children[ob].insert(otherNode)
            prevList.children[ob].parent = prevList
            otherNode.leafLL = prevList.children[ob]

            # print("inserted node : ", newNode.key, newNode.memvec)
            # print("other node : ", otherNode.key, otherNode.memvec)

        return True


    def delete(self, node):
        """
        Given a node, deletes it from the skip graph. Returns said node.
        """
        currList = node.leafLL
        while currList is not None:
            currList.delete(node.key)
            next = currList.parent
            if len(currList) == 0: # purge empty linked lists
                currList = None
            if currList is not None:
                for i in [0,1]: # purge redundant linked lists
                    child = currList.children[i]
                    if child is not None and child == currList:
                        gchild1 = child.children[1]
                        gchild0 = child.children[0]
                        currList.children[0] = gchild0
                        currList.children[1] = gchild1
                        if gchild0 is not None:
                            gchild0.parent = currList
                        if gchild1 is not None:
                            gchild1.parent = currList
                        l = currList.level  #amend memvecs, decrease height of LLs in subtree
                        currList.map(lambda n : n.remove_memvec_bit(l))
                        self.__height_decrementer_helper(currList.children[0])
                        self.__height_decrementer_helper(currList.children[1])
            currList = next

        node.leafLL = None

        return node


    def init_random(self, vals):
        """
        initializes a random skip graph with all keys in list vals
        """
        for i in vals:
            self.insert(i)

    def __height_decrementer_helper(self, LL):
        """
        decrements height in all linked lists from subtree rooted at LL
        """
        if LL is None:
            return
        LL.decrement_level_by_one()
        self.__height_decrementer_helper(LL.children[0])
        self.__height_decrementer_helper(LL.children[1])

    def visualize(self, path):
        """
        Creates png of skip graph, saves it to path (where path includes
        filename.png)
        """

        graph = pydot.Dot(rankdir = "BT", fontsize = "15")
        shape = "circle" if len(self.level0) == 1 else "box"
        node = pydot.Node(str(self.level0), shape = shape)
        graph.add_node(node)

        def helper(currLL, currLLnode):
            l = currLL.children[0]
            r = currLL.children[1]
            if l is not None:
                #assert(l != currLL)
                shape = "circle" if len(l) == 1 else "box"
                lnode = pydot.Node(str(l), shape = shape)
                edge = pydot.Edge(currLLnode, lnode, label = "0", arrowhead = "None")
                graph.add_node(lnode)
                graph.add_edge(edge)
                helper(l, lnode)
            if r is not None:
                #assert(r != currLL)
                shape = "circle" if len(r) == 1 else "box"
                rnode = pydot.Node(str(r), shape = shape)
                edge = pydot.Edge(currLLnode, rnode, label = "1", arrowhead= "None")
                graph.add_node(rnode)
                graph.add_edge(edge)
                helper(r, rnode)
            return

        helper(self.level0, node)
        graph.write_png(path)
        return graph

    def clear_and_fix_heights_LLs(self, startLL, level = 0):
        """
        clears contents of all LLs in the subskip graph rooted at startLL.
        Preserves structure, but deletes all nodes.
        Also fixes the heights.
        """
        if startLL is None:
            return
        else:
            startLL.clear()
            startLL.level = level
            left = startLL.children[0]
            right = startLL.children[1]
            l = self.clear_and_fix_heights_LLs(left, level = level+1)
            r = self.clear_and_fix_heights_LLs(right, level = level+1)

    def DFS(self, startLL, endLL, path = []):
        """
        Treats the skip graph as a tree and just performs a depth first search
        from startLL to endLL (which can be thought of as nodes in the tree)
        Returns the dfs path as a binary vector.
        """
        if startLL is None:
            return []
        if startLL is endLL:
            return path
        else:
            left = startLL.children[0]
            right = startLL.children[1]
            l = self.DFS(left, endLL, path = path + [0])
            r = self.DFS(right, endLL, path = path + [1])
            if len(l) == 0:
                return r
            return l

    def DFS_map(self, startLL, fn, depth = 1):
        """
        performs fn on each LL through a depth first search of the
        LLs starting at root startLL
        """
        if startLL is None:
            return
        else:
            fn(startLL, i = depth)
            left = startLL.children[0]
            right = startLL.children[1]
            l = self.DFS_map(left, fn, depth = depth + 1)
            r = self.DFS_map(right, fn, depth = depth + 1)

    def path_to_root_map(self, startLL, endLL, fn):
        """
        Calls fn on all linked lists on the path from startLL
        to endLL (not including endLL), in order from startLL to endLL
        """
        if startLL is endLL or startLL is None:
            return
        else:
            parent = startLL.parent
            fn(startLL)
            self.path_to_root_map(parent, endLL, fn)



    def get_all_leaves_with_path(self, fromLL):
        """
        Returns a dict where each LLnode in the subskip graph rooted at
        fromLL maps to their new memvec(at least the bits from fromLL to the leaf)
        as determined by the path from the root
        """
        dict = {}
        def helper(startLL, path = []):
            if startLL is None:
                return
            if startLL.children[0] is None and startLL.children[1] is None:
                assert(len(startLL) == 1)
                dict[startLL.head] = path
                return
            else:
                left = startLL.children[0]
                right = startLL.children[1]
                l = helper(left, path = path + [0])
                r = helper(right, path = path + [1])

        helper(fromLL)
        return dict

    def update_memvecs(self):
        """
        updates memvecs for each node.
        This is expensive, only do this if necessary (shouldn't be, unless insertion).
        Searching/deleting does not use memvecs. Only insertion does.
        """
        d = self.get_all_leaves_with_path(self.level0)
        for node in d:
            node.set_memvec(d[node])


    def swap(self, LL1, LL2):
        """
        swaps the two linked lists, as if the skip graph was a tree
        """
        if LL1.parent is not None:
            LL1_bit = 1 if LL1.parent.children[1] is LL1 else 0
            LL1.parent.children[LL1_bit] = LL2
        if LL2.parent is not None:
            LL2_bit = 1 if LL2.parent.children[1] is LL2 else 0
            LL2.parent.children[LL2_bit] = LL1

        LL1parent = LL1.parent
        LL2parent = LL2.parent
        LL1.parent = LL2parent
        LL2.parent = LL1parent

        LL1child0 = LL1.children[0]
        LL1child1 = LL1.children[1]
        LL2child0 = LL2.children[0]
        LL2child1 = LL2.children[1]

        LL1.children[0] = LL2child0
        if LL2child0 is not None:
            LL2child0.parent = LL1
        LL1.children[1] = LL2child1
        if LL2child1 is not None:
            LL2child1.parent = LL1
        LL2.children[0] = LL1child0
        if LL1child0 is not None:
            LL1child0.parent = LL2
        LL2.children[1] = LL1child1
        if LL1child1 is not None:
            LL1child1.parent = LL2

        if self.level0 is LL1:
            self.level0 = LL2
        elif self.level0 is LL2:
            self.level0 = LL1

    def insert_from(self, fromLL, node, suffix):
        """
        inserts node into skip graph starting from (and including) fromLL,
        and continues creating/inserting into higher level LLs based on
        suffix
        """
        startLL = fromLL
        level = startLL.level

        startLL.insert(node)
        level = level + 1
        for b in suffix:
            if startLL.children[b] is None:
                newLL = SortedLinkedList(level = level)
                startLL.children[b] = newLL
                newLL.parent = startLL
            startLL.children[b].insert(node)
            startLL = startLL.children[b]
            level += 1

        node.leafLL = startLL

    def get_node(self, key):
        """
        gets the node associated with key. (Not a skip graph operation,
        just for convenience/debugging purposes)
        """
        return self.level0.search(key, self.level0.head)

    def __str__(self):
        queue = [self.level0]
        d = {}
        while len(queue) > 0:
            ll = queue.pop(0)
            if ll is None:
                continue
            if ll.level not in d:
                d[ll.level] = [str(ll)]
            else:
                d[ll.level].append(str(ll))
            queue.append(ll.children[0])
            queue.append(ll.children[1])

        i = max(d)
        s = ''
        while i in d:
            s += "level " + str(i) + " "*2
            for sll in d[i]:
                s += sll + "\t"
            s += '\n'
            i -= 1
        return s

#
def generate_balanced_skipgraph(n, constructor = SkipGraph):
    """
    n is a power of 2. generates a skip graph that is completely balanced (all leaf nodes are same height)
    """
    l = int(math.log(n,2)) - 3
    mvecs = [[0,0,0],[1,0,0], [0,1,0], [1,1,0],[0,0,1], [0,1,1], [1,0,1], [1,1,1]]
    while l > 0:
        mvecs = [i + [0] for i in mvecs] + [i + [1] for i in mvecs]
        l -= 1
    S = constructor()
    for i in range(n):
        node = LLNode(i)
        node.set_memvec(mvecs[i])
        S.insert(node)
    return S

def generate_spine_skipgraph(n, constructor = SkipGraph):
    """
    Generates a skip graph on n nodes where every LL has a
    child that is a leaf list, hence the name : a spine
    """
    mvecs = [[0]*i + [1] for i in range(n-1)] + [[0]*(n-1)]
    S = constructor()
    for i in range(n):
        node = LLNode(i)
        node.set_memvec(mvecs[i])
        S.insert_from(S.level0, node, mvecs[i])
    return S

def generate_random_skipgraph(n, constructor = SkipGraph):
    """
    generates random skip graph on values in [0,...n-1]
    """
    S = constructor()
    S.init_random(list(range(n)))
    return S

if __name__ == "__main__":
    S = generate_spine_skipgraph(8, constructor = SkipGraph).visualize("before.png")
