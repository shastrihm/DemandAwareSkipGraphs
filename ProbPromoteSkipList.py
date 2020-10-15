from SkipList import SkipList, SortedLinkedList, LLNode
import random

class ProbPromoteSkipList(SkipList):
    """
    Variant of skip list that inserts all new nodes at the bottom level.
    When a node is searched for, it rises one level with probability p.
    """
    def __init__(self, p):
        SkipList.__init__(self, p)

    def insert(self, key):
        """
        Inserts key into skip list. Returns True for a successful insert.
        Otherwise return False if the key was already in the skip list.
        """
        newNode = LLNode(key)
        if not self.LLs[0].insert(newNode):
            return False
        self.update_head()

    def search(self, key):
        """
        Searches for key in skip list, and returns the node with that key if found,
        otherwise returns None.
        Promotes that node one level with probability self.p.
        If node is already at the top level, it is promoted only if it is not the only node at that level
        """
        node = super().search(key)
        if node is None:
            return None
        h = node.get_height()
        if random.uniform(0,1) < self.p and len(self.LLs[h]) > 1:
            self.promote(node)
        self.update_head()
        return node

    def promote(self, node):
        """
        increases node's height in skip list by one
        """
        h = node.get_height()
        if len(self.LLs) <= h + 1:
            s = SortedLinkedList(head = None, level = h + 1)
            s.insert(node)
            self.LLs.append(s)
            self.levels += 1
        else:
            self.LLs[h+1].insert(node)


