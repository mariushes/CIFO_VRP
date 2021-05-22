from random import uniform, sample, choice
from operator import attrgetter
import numpy as np

mo_functions = None

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

