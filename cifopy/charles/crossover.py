from random import randint, uniform, sample
import random
import numpy as np


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
    co_point = randint(1, len(p1)-2)

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
    alpha = uniform(0,1)
    # Take weighted sum of two parents, invert alpha for second offspring
    for i in range(len(p1)):
        offspring1[i] = p1[i] * alpha + (1 - alpha) * p2[i]
        offspring2[i] = p2[i] * alpha + (1 - alpha) * p1[i]

    return offspring1, offspring2


def pmx_co(p1, p2):
    # Sample 2 random co points
    co_points = sample(range(len(p1)), 2)
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
    """Implementation of ordered crossover

    Args:
        p1 (Individual): First parent for crossover.
        p2 (Individual): Second parent for crossover.

    Returns:
        Individuals: Two offspring, resulting from the crossover.
    """
    #sample 2 random co points
    co_points = sample(range(len(p1)), 2)
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

    #call the function twice with parents reversedd
    offspring1, offspring2 = (OX(p1,p2), OX(p2,p1))
    return offspring1, offspring2

def uniform_order_co(p1, p2):
    """Implementation of uniform order crossover

    Args:
        p1 (Individual): First parent for crossover.
        p2 (Individual): Second parent for crossover.

    Returns:
        Individuals: Two offspring, resulting from the crossover.
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
            offspring2[i]=p2[i]

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

        while len(offspring) < len(p1) - 1:
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

    offspring1, offspring2 = (EAX(p1, p2), EAX(p1, p2))
    return offspring1, offspring2



if __name__ == '__main__':
    p1 = [1,2,6,4,3,5,7]
    p2 = [7,2,5,3,4,6,1]

    print(edge_recombination_co(p1, p2))