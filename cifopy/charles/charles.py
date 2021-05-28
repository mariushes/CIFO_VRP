from charles.selection import fps
from random import shuffle, choice, sample, random
from operator import  attrgetter, index
from copy import deepcopy
import numpy as np

from charles.selection import multi_objective_dominant, is_pareto_efficient

import csv
import time
import os


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
        
        #for multi-objective optimization. Calculate second fitness function if it is monkeypatched
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

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"

    def append(self, appendix):
        self.representation.append(appendix)

    def insert(self, index, insert):
        self.representation.insert(index, insert)

    def pop(self, index=-1):
        temp = self.representation.pop()
        return temp




class Population:
    def __init__(self, size, optim, **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim

        self.pareto_flags = None

        self.gen = 1
        self.timestamp = int(time.time_ns())

        for _ in range(size):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"],
                    replacement=kwargs["replacement"],
                    valid_set=kwargs["valid_set"]
                )
            )
        #initial variance is needed when prem=True
        self.initial_var = np.var([i.fitness for i in self])
        #save the arguments needed to generate new random solutions
        self.sol_size = kwargs["sol_size"]
        self.replacement = kwargs["replacement"]
        self.valid_set = kwargs["valid_set"]
        
        
    def evolve(self, gens, select, crossover, mutate, co_p, mu_p, elitism, print_all_pareto=False, prem = False, log_only_last=True):
        for gen in range(gens):
            new_pop = []

            if elitism == True:
                if select == multi_objective_dominant:
                    # if the selection is multi objective we cannot choose the elites by the maximum fitness
                    # instead we take all pareto efficient elements as elites and save it in a list, which we insert later

                    # calculate the pareto efficient (non-dominated) individuals
                    costs = [[indiv.fitness, indiv.fitness2] for indiv in self]
                    costs = np.array(costs)
                    pareto_list = is_pareto_efficient(costs, self.optim).tolist()
                    elites = []

                    # add all pareto efficient elements to the elites
                    for i, pareto in enumerate(pareto_list):
                        if pareto:
                            elites.append(self[i])

                else:
                    if self.optim == "max":
                        elite = deepcopy(max(self.individuals, key=attrgetter("fitness")))
                    elif self.optim == "min":
                        elite = deepcopy(min(self.individuals, key=attrgetter("fitness")))
            
            # caluclate the variance for the entire population to lock it and check for premature convergence
            fitness = [i.fitness for i in self]
            var = np.var(fitness)
            
            if prem:
                #Check if it's reached premature convergence criteria by variance ratio
                if var/self.initial_var<0.05:
                    #print("Premature convergence! Reshuffling the deck")
                    self.reshuffle()
                    #Re-evaluate fitness since population changed
                    fitness = [i.fitness for i in self]
                    #print(f"New variance ratio:{np.var(fitness)/self.initial_var}")

            while len(new_pop) < self.size:
                parent1, parent2 = select(self), select(self)
                #Crossover
                if random() < co_p:
                    offspring1, offspring2 = crossover(parent1, parent2)
                    offspring1, offspring2 = crossover(parent1.representation, parent2.representation)
                else:
                    offspring1, offspring2 = parent1.representation, parent2.representation
                # Mutation
                if random() < mu_p:
                    offspring1 = mutate(offspring1)
                if random() < mu_p:
                    offspring2 = mutate(offspring2)

                new_pop.append(Individual(representation=offspring1))
                if len(new_pop) < self.size:
                    new_pop.append(Individual(representation=offspring2))


            #keep best individual if elitism==True
            if elitism == True:
                if select == multi_objective_dominant:
                    # for multi objective elitism we cannot just compute the max and the least
                    # before creating the new population we already saved all the pareto efficient as the elites
                    # here we replace any dominated individuals to by the elites

                    # calculate the pareto efficient (non-dominated) individuals
                    costs = [[indiv.fitness, indiv.fitness2] for indiv in self]
                    costs = np.array(costs)
                    pareto_list = is_pareto_efficient(costs, self.optim).tolist()

                    for i, pareto in enumerate(pareto_list):
                        # if there is no elites left break the loop
                        if not elites:
                            break
                        # get an element from the elites list and replace a non-pareto (dominated) inidividual by it
                        if not pareto:
                            self[i] = elites.pop()
                else:
                    if self.optim == "max":
                        least = min(new_pop, key=attrgetter("fitness"))
                    elif self.optim == "min":
                        least = max(new_pop, key=attrgetter("fitness"))
                    new_pop.pop(new_pop.index(least))
                    new_pop.append(elite)

            # log generation
            if log_only_last:
                if self.gen == gens:
                    self.log(select, crossover, mutate, gens, co_p, mu_p, elitism, prem, var)
            else:
                self.log(select, crossover, mutate, gens, co_p, mu_p, elitism, prem, var)

            self.individuals = new_pop

            # reset the pareto flags that are saved for the multi-objective selection for the previous population
            self.pareto_flags = None
            
            # if multi dominant objective is selection, save for indiv if it is pareto efficient which is needed for logging
            if select == multi_objective_dominant:
                # calculate the pareto efficient (non-dominated) individuals
                costs = [[indiv.fitness, indiv.fitness2] for indiv in self]
                costs = np.array(costs)
                pareto_list = is_pareto_efficient(costs, self.optim).tolist()

                # save the pareto booleans to the corresponding individuals 
                for i, pareto in enumerate(pareto_list):
                    self[i].pareto = pareto

            if self.gen % 100==0:
                if select == multi_objective_dominant:
                    # calculate the pareto efficient (non-dominated) individuals
                    costs = [[indiv.fitness, indiv.fitness2] for indiv in self]
                    costs = np.array(costs)
                    pareto_list = is_pareto_efficient(costs, self.optim).tolist()
                    
                    if print_all_pareto:
                        # print all elements that are pareto efficient 
                        print("")
                        for i, pareto in enumerate(pareto_list):
                            if pareto:
                                print(f'Best Individual: Fitness 1: {self[i].fitness}, Fitness 2: {self[i].fitness2}')
                    else:
                        #return the first element that is found to be pareto efficient 
                        pareto_index = pareto_list.index(True)
                        print(f'Best Individual: Fitness 1: {self[pareto_index].fitness}, Fitness 2: {self[pareto_index].fitness2}')
                    
                else:
                    if self.optim == "max":
                        print(f'Best Individual: {max(self, key=attrgetter("fitness"))}')
                    elif self.optim == "min":
                        print(f'Best Individual: {min(self, key=attrgetter("fitness"))}')
            

            self.gen += 1

    #when variance in the population is too low half of the population is discarded and replaced with
    #randomly generated individuals
    def reshuffle(self):
        n = len(self)
        new_pop = []
        #the best individual in the population is always saved
        if self.optim == "max":
            new_pop.append(deepcopy(max(self.individuals, key=attrgetter("fitness"))))
        elif self.optim == "min":
            new_pop.append(deepcopy(min(self.individuals, key=attrgetter("fitness"))))

        # append the half population that will be kept
        keep = sample(range(n), k=n//2)
        for i in keep:
            new_pop.append(deepcopy(self.individuals[i])) #to test, not sure
        # generate new random indivs until the size is reached
        while len(new_pop)<n:
            new_pop.append(Individual(
                    size=self.sol_size,
                    replacement=self.replacement,
                    valid_set=self.valid_set))

        self.individuals = new_pop

    #log the results
    def log(self, select, crossover, mutate, gens, co_p, mu_p, elitism, prem, var, log_representation = False):
        
        setup_string = select.__name__ + "-" + crossover.__name__ + "-" + mutate.__name__ + "-" + str(gens) + "-" + str(co_p) + "-" + str(mu_p) + "-" + str(elitism) + "-" + str(prem)
        dir_name = 'runs/' + setup_string
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(dir_name + "/run" + f'-{self.timestamp}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            for i in self:
                # if clauses that log different things depening on the settings and type of problem
                if log_representation:
                    if select == multi_objective_dominant:
                        writer.writerow([self.gen, i.representation, i.fitness, i.fitness2, i.pareto, var])
                    else:
                        writer.writerow([self.gen, i.representation, i.fitness,var])
                else:
                    if select == multi_objective_dominant:
                        #sometimes there is an error with the pareto values, then the logging is skipped
                        try:
                            writer.writerow([self.gen, i.fitness, i.fitness2, i.pareto, var])
                        except:
                            print("Error with logging")
                    else:
                        writer.writerow([self.gen, i.fitness,var])



    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]

    def __setitem__(self, position, value):
        self.individuals[position] = value

    def __repr__(self):
        return f"Population(size={len(self.individuals)}, individual_size={len(self.individuals[0])})"
