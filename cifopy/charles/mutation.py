from random import randint, sample, random

dm = None
home = None


def template_mutation(individual):
    """[summary]

    Args:
        individual ([type]): [description]

    Returns:
        [type]: [description]
    """
    return individual


def binary_mutation(individual):
    """Binary muation for a GA individual

    Args:
        individual (Individual): A GA individual from charles libray.py

    Raises:
        Exception: When individual is not binary encoded.py

    Returns:
        Individual: Mutated Individual
    """
    mut_point = randint(0, len(individual) - 1)

    if individual[mut_point] == 0:
        individual[mut_point] = 1
    elif individual[mut_point] == 1:
        individual[mut_point] = 0
    else:
        raise Exception(
            f"Trying to do binary mutation on {individual}. But it's not binary."
        )

    return individual


def swap_mutation(individual):
    # Get two mutation points
    mut_points = sample(range(len(individual)), 2)
    # Rename to shorten variable name
    i = individual

    i[mut_points[0]], i[mut_points[1]] = i[mut_points[1]], i[mut_points[0]]

    return i

def swap_sequence_mutation(individual):
    """
    Swap sequence mutation swaps two non-overlapping sequences in the offspring to generate a child.
    """
    i = individual

    # get two points as start points for the two sequences
    seq_points = sample(range(len(individual)), 2)

     # sort them 
    seq_points.sort()
    # the maximum sequence length is the minimum from the distance of the first to the second sequence point and the second to the end.
    max_len = min([seq_points[1] - seq_points[0] , len(i) - seq_points[1]])
    max_len = max([max_len,0])
    #sample the sequence length
    seq_len = sample(range(1,max_len+1), 1)[0]

    # sort them 


    i[seq_points[0]:seq_points[0]+seq_len], i[seq_points[1]:seq_points[1]+seq_len] = i[seq_points[1]:seq_points[1]+seq_len], i[seq_points[0]:seq_points[0]+seq_len]

    return i


def centre_inverse_mutation(individual):
    """
    https://arxiv.org/pdf/1203.3099.pdf
    The chromosome is divided into two sections. All genes in each section are copied and then inversely placed in the same section of a child.
    """
    i = individual

    centre = sample(range(len(i)), 1)[0]

    i[0:centre] = i[0:centre][::-1]
    i[centre:len(i)] = i[centre:len(i)][::-1]

    return i

def throas_mutation(individual):
    """
    https://arxiv.org/pdf/1203.3099.pdf
    We construct a sequence of three genes: the first is selected randomly and the two
    others are those two successors. Then, the last becomes the first of the sequence, the second becomes last and the first becomes the second in the sequence.
    """
    
    i = individual

    point = sample(range(len(i)-2), 1)[0]

    i[point], i[point+2] = i[point+2], i[point]

    return i

def partial_shuffle_mutation(individual):
    beta = 0.8
    i = individual
    for k in range(len(individual)):
        if random() > beta:
            point = sample(range(len(i)), 1)[0]
            i[k], i[point] = i[point], i[k]
    
    return i


def cheapest_insertion_mutation(individual):
    """
    Choose a random location in the individual and removes it. Inserts the location at the cheapest position.
    Not really a random mutation since it tries to optimize fitness by using the TSP heuristic.
    TODO: Finish
    """
    i = individual
    if dm == None:
        raise Exception("You need to monkey patch the distance matrix.")
    
    if home == None:
        raise Exception("You need to monkey patch the home.")
    insert_point = sample(range(len(i)), 1)
    insert = i.pop(insert_point[0])

    i.append(home)

    # Calculate cheapest detour
    cheapest_detour = 9999999
    cheapest_detour_pos = 0
    for j in range(len(i)):
        normal_length = dm[i[j-1]][i[j]]
        insert_length = dm[i[j-1]][insert] + dm[insert][i[j]]
        detour = insert_length - normal_length
        if detour < cheapest_detour:
            cheapest_detour = detour
            cheapest_detour_pos = j
        
    i.insert(cheapest_detour_pos, insert)
    if i.pop() != home:
        raise Exception("Last Element not home.")

    return i

def inversion_mutation(individual):
    i = individual
    # Position of the start and end of substring
    mut_points = sample(range(len(i)), 2)
    # This method assumes that the second point is after (on the right of) the first one
    # Sort the list
    mut_points.sort()
    # Invert for the mutation
    i[mut_points[0]:mut_points[1]] = i[mut_points[0]:mut_points[1]][::-1]

    return i
    
if __name__ == '__main__':
    i1 = [1,2,3,4,5,6]
    distance_matrix = [
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
    home = 0
    print(cheapest_insertion_mutation(i1))