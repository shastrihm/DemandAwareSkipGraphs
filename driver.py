"""
Driver.py

Given an access sequence X of inserts, searches, and deletes,
generates a sequence of images of how a Skip Graph evolves over time
"""
import moviepy.editor as mpy
import os
from SkipGraph import SkipGraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
import random

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

    def search(self, key, fromNode = None, needLL = False):
        v = self.S.search(key, fromNode, needLL)
        self.new_frame()
        return v

    def insert(self, key):
        v = self.S.insert(key)
        self.new_frame()
        return v

    def delete(self, node):
        v = self.S.delete(node)
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


if __name__ == "__main__":
    S = AdaptiveSkipGraphV1()
    D = Driver(S, "images")
    for i in range(10):
        D.insert(random.randint(0,50))
