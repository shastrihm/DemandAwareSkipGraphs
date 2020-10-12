import random
import networkx as nx
import matplotlib.pyplot as plt

"""
Class definitions for LLNode, SortedLinkedList, and SkipList 
"""

class LLNode:
    def __init__(self, key):
        self.key = key
        self.neighbors = {}

    def get_right_ptr(self, atlevel):
        return self.neighbors[atlevel][1]

    def get_left_ptr(self, atlevel):
        return self.neighbors[atlevel][0]

    def set_right_ptr(self, node, atlevel):
        if atlevel not in self.neighbors:
            self.neighbors[atlevel] = [None, node]
        else:
            self.neighbors[atlevel][1] = node

    def set_left_ptr(self, node, atlevel):
        if atlevel not in self.neighbors:
            self.neighbors[atlevel] = [node, None]
        else:
            self.neighbors[atlevel][0] = node

class SortedLinkedList:
    """
    Implementation of a doubly-linked sorted linked list.
    No duplicate keys are allowed.
    """
    def __init__(self, head = None, level = 0):
        self.level = level #for skip list purposes
        self.head = head
        self.len = 0 if head is None else 1

    def search(self, key, fromNode, insertion = False):
        """
        Starting from fromNode, searches for queried key.
        If key found, returns the Node with that key.
        if insertion = True:
            returns (x,y) that tells the insert method to insert
            the new node between x and y
        if insertion = False:
            returns the node N with key closest to the search key from the
            direction of fromNode
            e.g. if fromNode = 15, search key = 5, and
                            LL = [1,4,10,11,12,15,20],
                 Then N will be 10.

        If empty, returns None
        """
        while fromNode is not None:
            if fromNode.key == key:
                if insertion:
                    return (False, False)
                else:
                    return fromNode
            elif fromNode.key < key:
                next = fromNode.get_right_ptr(self.level)
                if next is None or next.key > key:
                    if insertion:
                        return (fromNode, next)
                    else:
                        return fromNode
                fromNode = next
            else:
                next = fromNode.get_left_ptr(self.level)
                if next is None or next.key < key:
                    if insertion:
                        return (next, fromNode)
                    else:
                        return fromNode
                fromNode = next

        if insertion:
            return (None, None)
        else:
            return None

    def insert(self, newNode):
        """
        inserts node into LL in the correct ordered spot.
        Returns True if key successfully inserted.
        Returns False is key was already in the LL.
        """
        key = newNode.key
        x,y = self.search(key, self.head, insertion = True)
        if x == False and y == False:
            return False

        newNode.set_left_ptr(x, self.level)
        newNode.set_right_ptr(y, self.level)

        if x is not None:
            x.set_right_ptr(newNode, self.level)
        else:
            self.head = newNode
        if y is not None:
            y.set_left_ptr(newNode, self.level)

        self.len += 1
        return True

    def delete(self, key):
        """
        deletes key in LL.
        If key deleted, return True
        If key not deleted (i.e. key wasn't in LL to begin with), return False

        """
        x = self.search(key, self.head, insertion = False)
        if x is None or x.key != key:
            return False
        l = x.get_left_ptr(self.level)
        r = x.get_right_ptr(self.level)

        x.set_left_ptr(None, self.level)
        x.set_right_ptr(None, self.level)

        if r is not None:
            r.set_left_ptr(l, self.level)
        if l is not None:
            l.set_right_ptr(r, self.level)
        else:
            self.head = r

        self.len -= 1
        return True

    def clear(self):
        """
        Resets LL to be empty
        """
        self.head = None
        self.len = 0

    def graphify(self):
        """
        returns a networkx graph representing this LL
        """
        G = nx.Graph()
        curr = self.head
        while curr is not None:
            G.add_node(curr.key)
            next = curr.get_right_ptr(self.level)
            if next is not None:
                G.add_edge(curr.key, next.key)
            curr = next
        return G

    def __len__(self):
        return self.len

    def __str__(self):
        l = []
        curr = self.head
        while curr is not None:
            l.append(curr.key)
            curr = curr.get_right_ptr(self.level)
        return str(l)


class SkipList:
    """
    A doubly-linked skiplist
    """
    def __init__(self, p = 0.5):
        self.LLs = [SortedLinkedList(head = None, level = 0)]
        self.head = None
        self.levels = 0 # 0 indexed. so if self.levels = n, there are physically
                        # n + 1 levels
        self.p = p

    def insert(self, key):
        """
        Inserts key into skip list. Returns True for a successful insert.
        Otherwise return False if the key was already in the skip list.
        """
        newNode = LLNode(key)
        if not self.LLs[0].insert(newNode):
            return False

        cflip = random.uniform(0,1)
        lev = 1
        while cflip < self.p:
            cflip = random.uniform(0,1)
            if lev > self.levels:
                self.LLs.append(SortedLinkedList(head = None, level = lev))
                self.levels += 1
                self.LLs[lev].insert(newNode)
                lev += 1
                break
            self.LLs[lev].insert(newNode)
            lev += 1

        self.update_head()

    def update_head(self):
        """
        removes all empty LLs in skip list, and updates head to be the head
        of the topmost LL
        """
        self.head = self.LLs[-1].head

    def search(self, key):
        """
        Searches for key in Skip list. Returns the node with that key if found, otherwise None.
        """
        if self.head is None:
            return None
        fromNode = self.head
        for LL in reversed(self.LLs):
            fromNode = LL.search(key, fromNode)
            if fromNode.key == key:
                return fromNode
        return None

    def delete(self, key):
        """
        Deletes key in skip list. Returns True if key was deleted, otherwise False (i.e. key was not in
        skip list to begin with).
        """
        flag = False
        for LL in self.LLs:
            deleted = LL.delete(key)
            flag = flag or deleted
            if not deleted:
                break # since higher lists won't contain key anymore
        if flag:
            self.LLs = [LL for LL in self.LLs if len(LL) > 0]
        self.update_head()
        return flag

    def visualize(self):
        x_coords = {}
        G = self.LLs[0].graphify()
        i = 0
        for n in G.nodes:
            x_coords[n] = i
            i += 1

        for LL in self.LLs:
            G = LL.graphify()
            positions = {n: (x_coords[n], LL.level) for n in G.nodes}
            nx.draw_networkx(G, pos = positions)
        plt.show()

    def __str__(self):
        s = ''
        for LL in self.LLs:
            s = str(LL) + '\n' + s
        return s

    def __len__(self):
        return len(self.LLs[0])


if __name__ == "__main__":
    SL = SkipList(p = 0.5)
    for i in range(20):
        x = random.randint(0,100)
        SL.insert(x)
    print(SL)
    SL.visualize()
