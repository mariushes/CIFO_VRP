from data.vr1 import CAPACITY, NODE_COORD_SECTION, DEMAND_SECTION 
import math
import numpy as np

class node:
    def __init__(self, number, x, y, w):
        self.number = number
        self.pos = np.array((x,y))
        self.w = w
    def distance(self, other):
        return np.linalg.norm(self.pos-other.pos)

node_list = []
for x in NODE_COORD_SECTION:
    node_list.append(node())


n = len(node_list)
ad_matrix = np.zeros(shape=(n,n))
for node1 in node_list:
    for node2 in node_list:
        node1.number = i
        node2.number = j
        ad_matrix[i, j] = node1.distance(node2)

weights = [None for i in range(n)]
for x in node_list:
    weights[x.number] = x.w
