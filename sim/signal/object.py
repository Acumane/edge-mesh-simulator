import os
import sys
import numpy as np

COMPONENT_PATH = os.path.join(sys.prefix, "murt-assets")

def read(filename):
    triangles = []
    vertices = []
    with open(filename) as file:
        for line in file:
            components = line.strip(" \n").split(" ")
            if components[0] == "f":
                indices = [int(c.split("/")[0]) - 1 for c in components[1:]]
                for i in range(len(indices) - 2):
                    triangles.append(indices[i: i + 3])
            elif components[0] == "v":  #
                vertex = [float(c) for c in components[1:]]
                vertices.append(vertex)

    return np.array(vertices), np.array(triangles)

class Object:
    def __init__(self, object_name, file_path=None, directory_path=None):
        self.object_name = object_name
        self.scale, self.translate, self.rotate = \
            [1, 1, 1], [0, 0, 0], [0, 0, 0]
        if file_path is None:
            try:
                if directory_path is None:
                    file_path = os.path.join(
                        COMPONENT_PATH, f"{object_name}.obj")
                else:
                    file_path = os.path.join(
                        directory_path, f"{object_name}.obj")
                self.vertices, self.triangles = read(file_path)
            except:
                print("Unknown file, please enter the file path for object.")

    def get_triangles(self):
        return self.vertices, self.triangles

    def resize(self, x, y, z):
        self.scale = (float(x), float(y), float(z))

    def reposition(self, x, y, z):
        self.translate = (float(x), float(y), float(z))

    def rotate_obj(self, x, y, z):
        self.rotate = (float(x), float(y), float(z))
