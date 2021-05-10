from data.vr1 import CAPACITY as cap, NODE_COORD_SECTION as coord, DEMAND_SECTION as dem
import math
import numpy as np

#
class node:
    def __init__(self, number, x, y, w):
        self.number = number-1
        self.pos = np.array((x,y))
        self.w = w
    def distance(self, other):
        return np.linalg.norm(self.pos-other.pos)

node_list = []
for x in coord:
    node_list.append(node(x, coord[x][0], coord[x][1], dem[x]))


n = len(node_list)
dist_matrix = [[None for i in range(n)] for i in range(n)]
for node1 in node_list:
    for node2 in node_list:
        i = node1.number
        j = node2.number
        dist_matrix[i][j] = node1.distance(node2)

weights = [None for i in range(n)]
for x in node_list:
    weights[x.number] = x.w
