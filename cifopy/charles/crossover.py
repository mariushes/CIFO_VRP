import random
import numpy as np
from random import randint, uniform, sample


dm = None
home = None

def template_co(p1, p2):
    """[summary]

    Args:
        p1 ([type]): [description]
        p2 ([type]): [description]

    Returns:
        [type]: [description]
    """

    #return offspring1, offspring2

def single_point_co(p1, p2):
    """Implementation of single point crossover.

    Args:
        p1 (Individual): First parent for crossover.
        p2 (Individual): Second parent for crossover.

    Returns:
        Individuals: Two offspring, resulting from the crossover.
    """
    co_point = random.randint(1, len(p1)-2)

    offspring1 = p1[:co_point] + p2[co_point:]
    offspring2 = p2[:co_point] + p1[co_point:]

    return offspring1, offspring2

def cycle_co(p1, p2):
    # Offspring placeholders - None values make it easy to debug for errors
    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p1)
    # While there are still None values in offspring, get the first index of
    # None and start a "cycle" according to the cycle crossover method
    while None in offspring1:
        index = offspring1.index(None)
        # alternate parents between cycles beginning on second cycle
        if index != 0:
            p1, p2 = p2, p1
        val1 = p1[index]
        val2 = p2[index]

        while val1 != val2:
            offspring1[index] = p1[index]
            offspring2[index] = p2[index]
            val2 = p2[index]
            index = p1.index(val2)
        # In case last values share the same index, fill them in each offspring
        offspring1[index] = p1[index]
        offspring2[index] = p2[index]

    return offspring1, offspring2

def arithmetic_co(p1, p2):
    # Offspring placeholders - None values make it easy to debug for errors
    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p1)
    # Set a value for alpha between 0 and 1
    alpha = random.uniform(0,1)
    # Take weighted sum of two parents, invert alpha for second offspring
    for i in range(len(p1)):
        offspring1[i] = p1[i] * alpha + (1 - alpha) * p2[i]
        offspring2[i] = p2[i] * alpha + (1 - alpha) * p1[i]

    return offspring1, offspring2


def pmx_co(p1, p2):
    # Sample 2 random co points
    co_points = random.sample(range(len(p1)), 2)
    co_points.sort()

    def PMX(x, y):
        # Create placeholder for offspring
        o = [None] * len(x)

        # Copy co segment into offspring
        o[co_points[0]:co_points[1]] = x[co_points[0]:co_points[1]]

        # Find set of values not in offspring from co segment in P2
        z = set(y[co_points[0]:co_points[1]]) - set(x[co_points[0]:co_points[1]])

        # Map values in set to corresponding position in offspring
        for i in z:
            temp = i
            index = y.index(x[y.index(temp)])
            while o[index] != None:
                temp = index
                index = y.index(x[temp])
            o[index] = i

        while None in o:
            index = o.index(None)
            o[index] = y[index]
        return o

    o1, o2 = (
        PMX(p1, p2),
        PMX(p2, p1)
    )

    return o1, o2

def ordered_co(p1, p2):
    """
    Implementation of Ordered Crossover. Ordered Crossover copies a part of the offspring chromosome from the first
    parent and constructs the remaining by following the order in the second parent starting from the index
    of the last copied node.
    """
    #sample 2 random co points
    co_points = random.sample(range(len(p1)), 2)
    co_points.sort()

    def OX(x,y):
        offspring = [None] * len(x)
        #copy co segment into offspring
        offspring[co_points[0]:co_points[1]] = x[co_points[0]:co_points[1]]

        #fill in remaining values
        temp = co_points[1]
        for i in range(len(y)):
            if (y[(co_points[1] +  i )%len(y)] not in x[co_points[0]:co_points[1]]):
                offspring[temp] = y[(co_points[1] +  i )%len(y)]
                temp = (temp +1)%len(offspring)

        return offspring

    #call the function twice with parents reversed
    offspring1, offspring2 = (OX(p1,p2), OX(p2,p1))
    return offspring1, offspring2

def uniform_order_co(p1, p2):
    """
    Implementation of Uniform Order Crossover. Uniform Order Crossover starts creating a random binary string of the
    same length of the parents. Then the first offspring preserves the nodes from the first parent where the binary
    string contains "1", while the second offspring preserves the nodes from the second parent where the binary string
    contains "0". Finally both the offsprings are filled following the order of the parent from which they have not
    yet inherited.
    """
    #binary string of the same length as parents
    mask = np.random.randint(2, size=len(p1))

    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p2)

    #copying the genes from the parents to the offsprings according to the generated mask
    for i in range(len(mask)):
        if mask[i]:
            offspring1[i] = p1[i]
        else:
            offspring2[i] = p2[i]

    #auxiliary function to fill offspring
    def fill_remaining(offspring, parent):
        temp = 0
        for i in range(len(offspring)):
            if offspring[i] is None:
                while parent[temp] in offspring:
                    temp += 1
                offspring[i] = parent[temp]
        return offspring

    # call the function twice with parents reversed
    offspring1, offspring2 = (fill_remaining(offspring1, p2), fill_remaining(offspring2, p1))
    return offspring1, offspring2

def edge_recombination_co(p1, p2):
    """
    Implementation of Edge Recombination Crossover. Edge Recombination Crossover is based on the adjacency matrix,
    which stores the neighbors of each node in any parent.Then, starting from one of the two initial cities of the parents,
    it adds at each step the city in the edgelist of the current node which has the fewest entries in its own edgelist.
    """
    #build adjacency matrix
    adj_matrix = {}
    for i in range(len(p1)):
        entry = p1[i]
        adj_matrix[entry] = [p1[i-1]]
        if i +1 == len(p1):
            adj_matrix[entry].append(p1[0])
        else:
            adj_matrix[entry].append(p1[i+1])

    for i in range(len(p2)):
        edges = [p2[i-1]]
        if i +1 == len(p2):
            edges.append(p2[0])
        else:
            edges.append(p2[i+1])
        for j in list(adj_matrix.keys()):
            if j == p2[i]:
                if edges[0] not in adj_matrix.get(j):
                    adj_matrix[j].append(edges[0])
                if edges[1] not in adj_matrix.get(j):
                    adj_matrix[j].append(edges[1])

    def EAX(p1,p2):
        offspring = []
        #first node from a random parent
        N = random.choice((p1[0], p2[0]))

        while (len(offspring) < len(p1) - 1):
            offspring.append(N)
            #remove N from all neighbor lists
            table = {}
            for j in list(adj_matrix.keys()):
                if N in adj_matrix[j]:
                    adj_matrix[j].remove(N)

            #find next node
            if adj_matrix[N]:
                table = dict((k, adj_matrix[k]) for k in adj_matrix[N])
                numb_neigh = {key: len(value) for key, value in table.items()}
                min_value = min(numb_neigh.values())
                result = [key for key, value in numb_neigh.items() if value == min_value]
                N = random.choice(result)
            else:
                N = random.choice([key for key in adj_matrix.keys() if key not in offspring])

        offspring.append(N)
        return offspring

    # call the function twice
    offspring1, offspring2 = (EAX(p1, p2), EAX(p1, p2))
    return offspring1, offspring2


def alternating_edges_co(p1, p2):
    """
    Implementation of Alternating Order Crossover. Alternating Edges Crossover starts by adding the first city of a
    parent to the offspring. It then adds the city that proceeds from the other parent then the city that proceeds
    from the first parent and so on.
    If the next city is already in the offspring we add a random city not already visited.
    """
    parents = [p1,p2]
    offspring1 = []
    offspring2 = []

    #append the first city
    offspring1.append(p1[0])
    offspring2.append(p2[0])

    def AEX(offspring, parents, currentparent):
        unvisited = parents[currentparent][1:] #list of unvisited cities
        while (len(offspring) < len(p1)):
            idx = parents[1-currentparent].index(offspring[len(offspring) - 1]) #index of the current city in the parent

            if (idx == len(p1) - 1):
                N = random.choice(unvisited) #if there is not a next city, choose a random one unvisited
            elif (parents[1-currentparent][idx+1] in offspring):
                N = random.choice(unvisited) #if the next city is already in the offspring, choose a random one unvisited
            else:
                N = parents[1 - currentparent][idx + 1]

            offspring.append(N)
            unvisited.remove(N)
            currentparent = 1 - currentparent #swap the parents

        return offspring

    # call the function twice with different currentparent
    offspring1 = AEX(offspring1, parents,0)
    offspring2 = AEX(offspring2, parents, 1)
    return offspring1, offspring2

def HGreX_co(p1, p2):
    """
    Implementation of Heuristic Greedy Crossovers. Heuristic Greedy Crossover starts by adding the first city of a
    parent to the offspring. It then always adds, if possible, the cheaper city of the two respective parent arcs.
    If both the next candidates cities are already in the offspring, it adds a random city not already visited.
    """

    def HGreX(x, y):
        offspring = []
        offspring.append(x[0])

        unvisited = x[1:] # append the first city
        candidates = [] #list of possible candidate cities


        while (len(offspring) < len(p1)):

            add_candidate(offspring, x, candidates)
            add_candidate(offspring, y, candidates)

            if candidates == [None, None]: #If no candidates have been found, choose a random unvisited city
                N = random.choice(unvisited)
            elif None not in candidates: #choose the city to which the distance from the current element is shorter
                if dm[offspring[- 1]][candidates[0]] < dm[offspring[- 1]][candidates[1]]:
                    N = candidates[0]
                else:
                    N = candidates[1]
            else: #If only one candidate is found, select it
                N = [z for z in candidates if z is not None][0]

            offspring.append(N)
            unvisited.remove(N)
            candidates.clear()

        return offspring

    # auxiliary function to find the candidate cities
    def add_candidate(offspring, parent, candidates):
        idx = parent.index(offspring[len(offspring) - 1])
        if (idx == len(p1) - 1):
            candidates.append(None)
        elif (parent[idx + 1] in offspring):
            candidates.append(None)
        else:
            candidates.append(parent[idx + 1])


    offspring1 = HGreX(p1, p2)
    offspring2 = HGreX(p2, p1)
    return offspring1, offspring2


if __name__ == '__main__':
    p1 = [1,2,6,4,3,5,7]
    p2 = [7,2,5,3,4,6,1]

    dm = [
        [0, 2451, 713, 1018, 1631, 1374, 2408, 213, 2571, 875, 1420, 2145, 1972],
        [2451, 0, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579],
        [713, 1745, 0, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260],
        [1018, 1524, 355, 0, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987],
        [1631, 831, 920, 700, 0, 663, 1021, 1769, 949, 796, 879, 586, 371],
        [1374, 1240, 803, 862, 663, 0, 1681, 1551, 1765, 547, 225, 887, 999],
        [2408, 959, 1737, 1395, 1021, 1681, 0, 2493, 678, 1724, 1891, 1114, 701],
        [213, 2596, 851, 1123, 1769, 1551, 2493, 0, 2699, 1038, 1605, 2300, 2099],
        [2571, 403, 1858, 1584, 949, 1765, 678, 2699, 0, 1744, 1645, 653, 600],
        [875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, 0, 679, 1272, 1162],
        [1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, 0, 1017, 1200],
        [2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, 0, 504],
        [1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, 0],
    ]

    print(HGreX_co(p1, p2))