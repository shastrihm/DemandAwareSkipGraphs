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
                    belongs in the Skip Graph
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
        Inserts key into skip graph.
        If key was already in the skip graph, does nothing and returns False
        """
        newNode = LLNode(key)
        if key in self.level0:
            return False

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


        return True


    def delete(self, node):
        """
        Given a node, deletes it from the skip graph.
        """
        currList = node.leafLL
        while currList is not None:
            currList.delete(node.key)
            currList = currList.parent
            # purge empty linked lists
            if currList is not None:
                if len(currList.children[0]) == 0:
                    currList.children[0] = None
                elif len(currList.children[1]) == 1:
                    currList.children[1] = NOne

        node.leafLL = None

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
                shape = "circle" if len(l) == 1 else "box"
                lnode = pydot.Node(str(l), shape = shape)
                edge = pydot.Edge(currLLnode, lnode, label = "0", arrowhead = "None")
                graph.add_node(lnode)
                graph.add_edge(edge)
                helper(l, lnode)
            if r is not None:
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
