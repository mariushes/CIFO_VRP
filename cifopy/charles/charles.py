from random import shuffle, choice, sample, random
from operator import  attrgetter, index
from copy import deepcopy
from charles.selection import multi_objective_dominant, is_pareto_efficient
import numpy as np


class Individual:
    def __init__(
        self,
        representation=None,
        size=None,
        replacement=True,
        valid_set=[i for i in range(13)],
    ):
        if representation == None:
            if replacement == True:
                self.representation = [choice(valid_set) for i in range(size)]
            elif replacement == False:
                self.representation = sample(valid_set, size)
        else:
            self.representation = representation
        self.fitness = self.evaluate()
        
        try:
            self.fitness2 = self.evaluate2()
        except:
            pass

    def evaluate(self):
        raise Exception("You need to monkey patch the fitness path.")

    def evaluate2(self):
        raise Exception("You need to monkey patch the fitness path.")

    def get_neighbours(self, func, **kwargs):
        raise Exception("You need to monkey patch the neighbourhood function.")

    def index(self, value):
        return self.representation.index(value)

    def __len__(self):
        return len(self.representation)

    def __getitem__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value
        self.fitness = self.evaluate()

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"

    def append(self, appendix):
        self.representation.append(appendix)
        self.fitness = self.evaluate()

    def insert(self, index, insert):
        self.representation.insert(index, insert)

    def pop(self, index=-1):
        temp = self.representation.pop()
        self.fitness = self.evaluate()
        return temp

    


class Population:
    def __init__(self, size, optim, **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim
        self.pareto_flags = None
        for _ in range(size):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"],
                    replacement=kwargs["replacement"],
                    valid_set=kwargs["valid_set"],
                )
            )
    def evolve(self, gens, select, crossover, mutate, co_p, mu_p, elitism, print_all_pareto=False):
        for gen in range(gens):
            new_pop = []
 
            if elitism == True:
                if self.optim == "max":
                    elite = deepcopy(max(self.individuals, key=attrgetter("fitness")))
                elif self.optim == "min":
                    elite = deepcopy(min(self.individuals, key=attrgetter("fitness")))
 
            while len(new_pop) < self.size:
                parent1, parent2 = select(self), select(self)
                # Crossover
                if random() < co_p:
                    offspring1, offspring2 = crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1, parent2
                # Mutation
                if random() < mu_p:
                    offspring1 = mutate(offspring1)
                if random() < mu_p:
                    offspring2 = mutate(offspring2)
 
                new_pop.append(Individual(representation=offspring1))
                if len(new_pop) < self.size:
                    new_pop.append(Individual(representation=offspring2))
 
            if elitism == True:
                if self.optim == "max":
                    least = min(new_pop, key=attrgetter("fitness"))
                elif self.optim == "min":
                    least = max(new_pop, key=attrgetter("fitness"))
                new_pop.pop(new_pop.index(least))
                new_pop.append(elite)
 
            self.individuals = new_pop
            self.pareto_flags = None

            if select == multi_objective_dominant:
                # if selection is by multi_objective_dominant we return the first element that is found to be pareto efficient 
                # by search for an element with the maximum flag.
                costs = [[indiv.fitness, indiv.fitness2] for indiv in self]
                costs = np.array(costs)
                pareto_list = is_pareto_efficient(costs, self.optim).tolist()
                
                pareto_index = pareto_list.index(True)
                print(f'Best Individual: Fitness 1: {self[pareto_index].fitness}, Fitness 2: {self[pareto_index].fitness2}')
                if print_all_pareto:
                    print("")
                    for i, pareto in enumerate(pareto_list):
                        if pareto:
                            print(f'Best Individual: Fitness 1: {self[i].fitness}, Fitness 2: {self[i].fitness2}')
                else:
                    pareto_index = pareto_list.index(True)
                    print(f'Best Individual: Fitness 1: {self[pareto_index].fitness}, Fitness 2: {self[pareto_index].fitness2}')
                
            else:
                if self.optim == "max":
                    
                    print(f'Best Individual: {max(self, key=attrgetter("fitness"))}')
                elif self.optim == "min":
                    print(f'Best Individual: {min(self, key=attrgetter("fitness"))}')
            

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]

    def __repr__(self):
        return f"Population(size={len(self.individuals)}, individual_size={len(self.individuals[0])})"
