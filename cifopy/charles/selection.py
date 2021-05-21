from random import uniform, sample
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
        """
        if prem:
            #Do we want to save this variance? Maybe we can plot how it changes through generation
            var = np.var(fitness)
            if var/population.initial_var<0.05:
                print("Premature convergence! Reshuffling the deck")
                population.reshuffle()
                #Re-evaluate fitness since population changed
                fitness = [i.fitness for i in population]"""
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
        raise NotImplementedError

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
