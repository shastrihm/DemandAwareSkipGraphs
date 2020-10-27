from SortedLinkedList import LLNode, SortedLinkedList
import random
import os
import pydot

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
            prevList.children[nb] = SortedLinkedList(level = i)
            prevList.children[nb].insert(newNode)
            prevList.children[nb].parent = prevList
            newNode.leafLL = prevList.children[nb]

            assert(len(prevList) == 2)
            if prevList.head == newNode:
                otherNode = prevList.head.get_right_ptr(i - 1)
            else:
                otherNode = prevList.head
            ob = nb ^ 1
            prevList.children[ob] = SortedLinkedList(level = i)
            prevList.children[ob].insert(otherNode)
            prevList.children[ob].parent = prevList
            otherNode.leafLL = prevList.children[ob]
            otherNode.add_memvec_bit(ob)


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
                assert(l != currLL)
                shape = "circle" if len(l) == 1 else "box"
                lnode = pydot.Node(str(l), shape = shape)
                edge = pydot.Edge(currLLnode, lnode, label = "0", arrowhead = "None")
                graph.add_node(lnode)
                graph.add_edge(edge)
                helper(l, lnode)
            if r is not None:
                assert(r != currLL)
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


if __name__ == "__main__":
    S = SkipGraph()
    for i in range(10):
        S.insert(random.randint(0,1000))
    S.visualize()
