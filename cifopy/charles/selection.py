from random import uniform, sample, choice
from operator import attrgetter
import numpy as np


def fps(population):
    """Fitness proportionate selection implementation.

    Args:
        population (Population): The population we want to select from.
        prem: By default False, in case the variance of the fitness distribution in the population is less than
        5% of the initial variance

    Returns:
        Individual: selected individual.
    """

    if population.optim == "max":
        # Sum total fitnesses
        fitness = [i.fitness for i in population]
        total_fitness = sum(fitness)
        # Get a 'position' on the wheel
        spin = uniform(0, total_fitness)
        position = 0
        # Find individual in the position of the spin
        for individual in population:
            position += individual.fitness
            if position > spin:
                return individual
    elif population.optim == "min":
        pop_fitness = [i.fitness for i in population]
        M, m = max(pop_fitness), min(pop_fitness)
        #min_prob is the probability of the least likely individual in a max instance with same fitness
        min_prob = m/sum(pop_fitness)
        n = len(population)
        #covering the (extremely unlikely) case where all indiv have the same fitness, that otherwise would bring
        # a division by zero
        if n*min_prob == 1:
            return choice(population.individuals)
        rev_fitness = [M-x for x in pop_fitness]
        to_add = min_prob*sum(rev_fitness)/(1-n*min_prob)
        #the new vector from which compute probabilities
        rev_fitness[:] = [x+to_add for x in rev_fitness]
         # Sum total fitnesses
        total_fitness = sum(rev_fitness)
        # Get a 'position' on the wheel
        spin = uniform(0, total_fitness)
        position = 0
        i = 0
        # Find individual in the position of the spin
        for individual in population:
            position += rev_fitness[i]
            if position > spin:
                return individual
            i += 1

    else:
        raise Exception("No optimiziation specified (min or max).")

def tournament(population, size=20):
    # Select individuals based on tournament size
    tournament = sample(population.individuals, size)
    # Check if the problem is max or min
    if population.optim == 'max':
        return max(tournament, key=attrgetter("fitness"))
    elif population.optim == 'min':
        return min(tournament, key=attrgetter("fitness"))
    else:
        raise Exception("No optimiziation specified (min or max).")


def multi_objective_dominant(population):

    # check if pareto flags were not already saved
    if population.pareto_flags == None:
        # Copy all indices into a set s
        population_indices = [*range(len(population))]
        costs = [[indiv.fitness, indiv.fitness2] for indiv in population]
        costs = np.array(costs)
        flags = [0 for i in population_indices]
        flag_count = 0

        # repeat
        while population_indices:
            flag_count += 1
            # find all non-dominant indices
            pareto_list = is_pareto_efficient(costs, population.optim)
            for i in range(len(pareto_list)):
                    # assign all non-dominated indices a flag
                if pareto_list[i]:
                    real_index = population_indices[i]
                    flags[real_index] = flag_count
            
            removed_elements = 0
            for i in range(len(pareto_list)):
                    # remove those indices from S
                if pareto_list[i]:
                    population_indices.pop(i-removed_elements)
                    costs = np.delete(costs, i-removed_elements, 0)
                    removed_elements += 1

        
        # selection probability: inversly to flag

        # inverse flag
        flag_range_reverse = [*range(flag_count,0,-1)]

        # can we save the flags in the population? Probably need a flag to indicate new generation
        
        for i in range(len(flags)):
            flags[i] = flag_range_reverse[flags[i]-1]
        population.pareto_flags = flags

    else:
        # assign pareto flags of population to flags variable if not there yet
        flags = population.pareto_flags
    
    sum_flags = sum(flags)

    spin = uniform(0, sum_flags)
    position = 0
    # Find individual in the position of the spin
    for flag, individual in zip(flags, population):
        position += flag
        if position > spin:
            return individual

def is_pareto_efficient(costs, optim,return_mask = True):
    """
    Find the pareto-efficient points
    From https://stackoverflow.com/questions/32791911/fast-calculation-of-pareto-front-in-python
    :param costs: An (n_points, n_costs) array
    :param return_mask: True to return a mask
    :return: An array of indices of pareto-efficient points.
        If return_mask is True, this will be an (n_points, ) boolean array
        Otherwise it will be a (n_efficient_points, ) integer array of indices.
    """
    is_efficient = np.arange(costs.shape[0])
    n_points = costs.shape[0]
    next_point_index = 0  # Next index in the is_efficient array to search for
    while next_point_index<len(costs):
        if optim =="max":
            nondominated_point_mask = np.any(costs>costs[next_point_index], axis=1)
        elif optim =="min":
            nondominated_point_mask = np.any(costs<costs[next_point_index], axis=1)
        nondominated_point_mask[next_point_index] = True
        is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
        costs = costs[nondominated_point_mask]
        next_point_index = np.sum(nondominated_point_mask[:next_point_index])+1
    if return_mask:
        is_efficient_mask = np.zeros(n_points, dtype = bool)
        is_efficient_mask[is_efficient] = True
        return is_efficient_mask
    else:
        return is_efficient

def rank(population):
    # Rank individuals based on optim approach
    if population.optim == 'max':
        population.individuals.sort(key=attrgetter('fitness'))
    elif population.optim == 'min':
        population.individuals.sort(key=attrgetter('fitness'), reverse=True)

    # Sum all ranks
    total = sum(range(population.size+1))
    # Get random position
    spin = uniform(0, total)
    position = 0
    # Iterate until spin is found
    for count, individual in enumerate(population):
        position += count + 1
        if position > spin:
            return individual

