"""
Driver.py

Given an access sequence X of inserts, searches, and deletes,
generates a sequence of images of how a Skip Graph evolves over time
"""
import moviepy.editor as mpy
import os
from SkipGraph import SkipGraph
from SkipGraph import generate_balanced_skipgraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
from ProbDemoteSkipGraph import ProbDemoteSkipGraph
import random
import generator

class Driver:
    """
    Wrapper over any Skip Graph API that generates images that depict the data structure
    adapting over time
    """
    def __init__(self, SkipGraph, path):
        self.S = SkipGraph
        self.ims = []
        self.path = path
        self.S.visualize(path = self.path + os.sep +"0.png")
        self.ims.append(self.path + os.sep + "0.png")

    def new_frame(self):
        self.S.visualize(path = self.path + os.sep + str(len(self.ims)) + ".png")
        self.ims.append(self.path + os.sep + str(len(self.ims)) + ".png")

    def search(self, key, fromNode = None, needLL = False, suppress = False):
        v = self.S.search(key, fromNode, needLL)
        if not suppress:
            self.new_frame()
        return v

    def insert(self, key, suppress = False):
        v = self.S.insert(key)
        if not suppress:
            self.new_frame()
        return v

    def delete(self, node, suppress = False):
        v = self.S.delete(node)
        if not suppress:
            self.new_frame()
        return v

    def reset(self):
        self.ims = []

    def output_gif(self, path = None):
        """
        TODO : fix so each image generated is of same size, so gif generation works
        """
        if path is None:
            path = "output.gif"

        gif_name = 'outputName'
        fps = 55
        clip = mpy.ImageSequenceClip(self.ims, fps=fps)
        clip.write_gif('{}.gif'.format(path), fps=fps)

    def simulate(self, distribution, samples = 1000, suppress = True):
        """
        Simulates communication requests sampled from distribution on the skip graph
        Distribution assigns a weight to every ordered (u,v) pair
        """
        reqs = generator.custom_distribution_demand_generator(distribution, samples)
        for r in reqs:
            u,v = r
            self.search(key = v,fromNode = u, suppress = suppress)

        if suppress:
            self.new_frame()



if __name__ == "__main__":
    N = 8
    thresh = 4
    SAMPLES = 100
    p = 0.5
    S = generate_balanced_skipgraph(N, constructor = ProbDemoteSkipGraph)
    #S = ProbDemoteSkipGraph()
    #S.init_random(list(range(N)))
    S.set_p(p)
    D = Driver(S, "probDemote")

    for req in generator.repeated_source_demand_generator(N-1, 0, SAMPLES):
        u,v = req
        print(req)
        D.search(v, u, suppress = True)
    D.new_frame()
