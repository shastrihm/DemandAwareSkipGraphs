import pydot
import os
"""
Code to generate specific figures for thesis
"""

def doubly_linkedlist(L, outfile):
    graph = pydot.Dot(rankdir= "LR", fontsize = "12")
    node = pydot.Node("HEAD", shape = "circle", fixedsize="True")
    graph.add_node(node)
    for i in L:
        newnode = pydot.Node(str(i), shape = "circle",  fixedsize="True")
        graph.add_node(node)
        edge = pydot.Edge(node, newnode)
        graph.add_edge(edge)
        edge = pydot.Edge(newnode, node)
        graph.add_edge(edge)
        node = newnode
    tail = pydot.Node("TAIL", shape = "circle",  fixedsize="True")
    graph.add_node(tail)
    graph.add_edge(pydot.Edge(node, tail))
    graph.add_edge(pydot.Edge(tail, node))
    graph.write_pdf(outfile)


doubly_linkedlist([0,1,2,3,4], "images" + os.sep + "doublyLL.pdf")
