from data.vr1 import CAPACITY as cap, NODE_COORD_SECTION as coord, DEMAND_SECTION as dem
import math
import numpy as np
"""
    each node has a position (two coordinates), a weight (which represents the demand of the node)
    and a number (since list indexing in python starts from 0 we decided to subtract 1 to the node 
    number in the original dataset)
"""
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
#compute distance matrix of the problem
dist_matrix = [[None for i in range(n)] for i in range(n)]
for node1 in node_list:
    for node2 in node_list:
        i = node1.number
        j = node2.number
        dist_matrix[i][j] = node1.distance(node2)

print(f"Total distance: {sum(sum(np.array(dist_matrix)))}")

"""for multi objective optimization we generate the amount of CO2 needed for each route. The CO2 has
exponential distribution with scale (and indeed mean) equal to the lenght of the route.
In this way CO2 and distance should have a similar magnitude."""

np.random.seed(seed = 42)
co2_matrix = [[None for i in range(n)] for i in range(n)]
for i in range(n):
    for j in range(i,n):
        if i == j:
            co2_matrix[i][j] = 0.0
        else:
            poll = np.random.exponential(scale = dist_matrix[i][j])
            co2_matrix[i][j] = poll
            co2_matrix[j][i] = poll
print(f"Total CO2: {sum(sum(np.array(co2_matrix)))}")
#fill in the demands vector
weights = [None for i in range(n)]
for x in node_list:
    weights[x.number] = x.w

capacity = cap
