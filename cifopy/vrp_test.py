from data.vrp_data import capacity, demands, distance_matrix, home
from charles.charles import Population, Individual
from charles.search import hill_climb, sim_annealing
from charles.selection import fps, tournament
from charles.mutation import swap_mutation
from charles.crossover import cycle_co

from vrp import evaluate, get_neighbours

Individual.evaluate = evaluate
Individual.get_neighbours = get_neighbours

test_ind = Individual(representation=[1,2,3,4,5,6,7,8])
print(test_ind.fitness)
test_ind[0] = 5
print(test_ind.fitness)
