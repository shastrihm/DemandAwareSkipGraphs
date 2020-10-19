import math
from io import StringIO

def show_tree(tree, total_width=60, fill=' '):
    """https://www.w3resource.com/python-exercises/heap-queue-algorithm/python-heapq-exercise-19.php"""
    """returns a string Pretty-print a tree.
    total_width depends on your input size"""
    output = StringIO()
    last_row = -1
    for i, n in enumerate(tree):
        if i:
            row = int(math.floor(math.log(i+1, 2)))
        else:
            row = 0
        if row != last_row:
            output.write('\n')
        columns = 2**row
        col_width = int(math.floor((total_width * 1.0) / columns))
        output.write(str(n).center(col_width, fill))
        last_row = row
    return output.getvalue()
