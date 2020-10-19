from SortedLinkedList import *

"""
Class definitions for LLNode, SortedLinkedList, and SkipList
"""

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
    for i in range(10):
        x = random.randint(0,100)
        SL.insert(x)
    print(SL)
    fig = SL.visualize()
