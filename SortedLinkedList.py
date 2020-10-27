import random


class LLNode:
    def __init__(self, key):
        self.key = key
        self.neighbors = {}
        self.leafLL = None
        self.memvec = []

    def get_memvec_bit(self, i):
        while len(self.memvec) - 1 < i:
            self.memvec.append(random.choice([0,1]))
        return self.memvec[i]

    def set_memvec_bit(self, i, newbit):
        while len(self.memvec) - 1 < i:
            self.memvec.append(random.choice([0,1]))
        self.memvec[i] = newbit

    def add_memvec_bit(self, newbit):
        self.memvec.append(newbit)

    def set_memvec(self, other_memvec):
        self.memvec = other_memvec.copy()

    def get_memvec(self):
        return self.memvec

    def remove_memvec_bit(self, i):
        return self.memvec.pop(i)

    def memvec_len(self):
        return len(self.memvec)

    def get_height(self):
        return max(self.neighbors)

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

    def clear_level(self, level):
        self.neighbors.pop(level, None)

    def reset(self):
        self.neighbors = {}
        self.leafLL = None
        self.memvec = []

class SortedLinkedList:
    """
    Implementation of a doubly-linked sorted linked list.
    No duplicate keys are allowed.
    """
    def __init__(self, head = None, level = 0):
        self.level = level #for skip graph purposes
        self.head = head
        self.children = [None, None] # for use in skip graph
        self.parent = None # for use in skip graph
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

    def as_list(self):
        l = []
        curr = self.head
        while curr is not None:
            l.append(curr)
            curr = curr.get_right_ptr(self.level)
        return l

    def decrement_level_by_one(self):
        curr = self.head
        while curr is not None:
            l = curr.get_left_ptr(self.level)
            r = curr.get_right_ptr(self.level)
            curr.set_right_ptr(r, self.level - 1)
            curr.set_left_ptr(l, self.level - 1)
            next = curr.get_right_ptr(self.level)
            curr.clear_level(self.level)
            curr = next
        self.level -= 1

    def map(self, fn):
        """
        applies fn to every node in the LL
        """
        curr = self.head
        while curr is not None:
            fn(curr)
            curr = curr.get_right_ptr(self.level)

    def __len__(self):
        return self.len

    def __str__(self):
        curr = self.head
        s = ''
        while curr is not None:
            s = s + str(curr.key) + "―"
            curr = curr.get_right_ptr(self.level)
        rs = s[:len(s)-1]
        if len(rs) == 0:
            return " "
        return rs

    def __contains__(self, key):
        n = self.search(key, self.head)
        return (n is not None and n.key == key)

    def __eq__(self, other):
        return self.as_list() == other.as_list()
