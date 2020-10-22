"""
Driver.py

Given an access sequence X of inserts, searches, and deletes,
generates an animated gif of how a Skip Graph evolves over X
"""
import imageio
import os
import shutil
from SkipGraph import SkipGraph
from AdaptiveSkipGraph_v1 import AdaptiveSkipGraphV1
import random

class Driver:
    def __init__(self, SkipGraph):
        self.S = SkipGraph
        self.ims = []
        self.path = 'images' + os.sep
        self.S.visualize(path = self.path + "0.png")
        self.ims.append(self.path + "0.png")

    def new_frame(self):
        self.S.visualize(path = self.path + str(len(self.ims)) + ".png")
        self.ims.append(self.path + str(len(self.ims)) + ".png")

    def search(self, key, fromNode = None, needLL = False):
        self.S.search(key, fromNode, needLL)
        self.new_frame()

    def insert(self, key):
        self.S.insert(key)
        self.new_frame()

    def delete(self, node):
        self.S.delete(node)
        self.new_frame()

    def reset(self):
        self.ims = []
        
    def output_gif(self, path = None):
        if path is None:
            path = "output.gif"

        png_dir = self.path
        images = []
        for file_path in self.ims:
            images.append(imageio.imread(file_path))
        imageio.mimsave(path, images)



if __name__ == "__main__":
    D = Driver(SkipGraph())
    for i in range(10):
        D.insert(random.randint(0,1000))
    D.output_gif()
