from random import randint, sample, random

dm = None
home = None


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

    # swap the sequences
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
    "We construct a sequence of three genes: the first is selected randomly and the two
    others are those two successors. Then, the last becomes the first of the sequence, the second becomes last and the first becomes the second in the sequence."
    """
    
    i = individual

    point = sample(range(len(i)-2), 1)[0]

    i[point], i[point+2] = i[point+2], i[point]

    return i

def partial_shuffle_mutation(individual):
    """
    https://arxiv.org/pdf/1203.3099.pdf
    Select each gene with a probability of beta and swap it with another random gene
    """
    beta = 0.1
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
    """

    # It needs the distance matrix and home to be monkey patched before
    if dm == None:
        raise Exception("You need to monkey patch the distance matrix.")
    if home == None:
        raise Exception("You need to monkey patch the home.")

    i = individual

    # randomly selecte element to be reinserted and remove it
    insert_point = sample(range(len(i)), 1)
    insert = i.pop(insert_point[0])

    # add home location to be able to calculate distance to home
    i.append(home)

    # Calculate cheapest detour
    cheapest_detour = 9999999
    cheapest_detour_pos = 0
    for j in range(len(i)):
        # calculate detour when inserting between node j and previous node
        normal_length = dm[i[j-1]][i[j]]
        insert_length = dm[i[j-1]][insert] + dm[insert][i[j]]
        detour = insert_length - normal_length

        # save detour position and value when cheaper than previous
        if detour < cheapest_detour:
            cheapest_detour = detour
            cheapest_detour_pos = j
    
    # insert at cheapest detour
    i.insert(cheapest_detour_pos, insert)

    # remove home again
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
    