from SortedLinkedList import LLNode, SortedLinkedList
import random

class SkipGraph:
    def __init__(self):
        self.level0 = SortedLinkedList()

    def search(self, key, fromNode = None):
        """
        returns node with key. Otherwise returns None
        fromNode: node to start search from. Must be a node that
                    belongs in the Skip Graph
        """
        if fromNode is None:
            fromNode = self.level0.head
            if fromNode is None:
                return None

        fromLL = fromNode.leafLL

        while fromLL is not None:
            fromNode = fromLL.search(key, fromNode)
            if fromNode.key == key:
                return fromNode
            fromLL = fromLL.parent

        return None

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

        return True


    def delete(self, node):
        """
        deletes node with key from the Skip Graph
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
        S.insert(random.randint(0,50))
