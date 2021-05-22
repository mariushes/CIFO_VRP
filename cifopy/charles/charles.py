from charles.selection import fps
from random import shuffle, choice, sample, random
from operator import  attrgetter
from copy import deepcopy
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

    def evaluate(self):
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
        for _ in range(size):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"],
                    replacement=kwargs["replacement"],
                    valid_set=kwargs["valid_set"]
                )
            )
        self.initial_var = np.var([i.fitness for i in self])
        self.sol_size = kwargs["sol_size"]
        self.replacement = kwargs["replacement"]
        self.valid_set = kwargs["valid_set"]
    def evolve(self, gens, select, crossover, mutate, co_p, mu_p, elitism, prem = False):
        for gen in range(gens):
            new_pop = []
 
            if elitism == True:
                if self.optim == "max":
                    elite = deepcopy(max(self.individuals, key=attrgetter("fitness")))
                elif self.optim == "min":
                    elite = deepcopy(min(self.individuals, key=attrgetter("fitness")))

            if prem and select == fps:
            #Do we want to save this variance? Maybe we can plot how it changes through generation
                fitness = [i.fitness for i in self]
                var = np.var(fitness)
                if var/self.initial_var<0.05:
                    print("Premature convergence! Reshuffling the deck")
                    self.reshuffle()
                    #Re-evaluate fitness since population changed
                    fitness = [i.fitness for i in self]
                    print(f"New variance ratio:{np.var(fitness)/self.initial_var}")

            while len(new_pop) < self.size:
                parent1, parent2 = select(self), select(self)
                #Crossover
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
 
            if self.optim == "max":
                if gen%50==0:
                    print(f'Best Individual: {max(self, key=attrgetter("fitness"))} Gen: {gen}')
 
            elif self.optim == "min":
                if gen%50==0:
                    print(f'Best Individual: {min(self, key=attrgetter("fitness"))} Gen: {gen}')
    
    def reshuffle(self):
        n = len(self)
        new_pop = []
        if self.optim == "max":
            new_pop.append(deepcopy(max(self.individuals, key=attrgetter("fitness"))))
        elif self.optim == "min":
            new_pop.append(deepcopy(min(self.individuals, key=attrgetter("fitness"))))
        
        
        keep = sample(range(n), k=n//2)
        #for how it's implemented the best could appear twice. Don't think it's a problem but we can avoid it
        #half of the times you keep the best twice, could also be useful. write in report
        for i in keep:
            new_pop.append(deepcopy(self.individuals[i])) #to test, not sure
        while len(new_pop)<n:
            new_pop.append(Individual(
                    size=self.sol_size,
                    replacement=self.replacement,
                    valid_set=self.valid_set))

        self.individuals = new_pop

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]

    def __repr__(self):
        return f"Population(size={len(self.individuals)}, individual_size={len(self.individuals[0])})"
