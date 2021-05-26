import data.vrp_data
import nodes
from charles.charles import Population, Individual
from charles.search import hill_climb, sim_annealing
from charles.selection import fps, tournament, multi_objective_dominant, rank
from charles.mutation import swap_mutation, cheapest_insertion_mutation, throas_mutation, inversion_mutation
import charles.mutation as mut
import charles.selection as sel
import charles.crossover as co
from charles.crossover import cycle_co, edge_recombination_co, HGreX_co, alternating_edges_co, ordered_co
from joblib import Parallel, delayed
import time


dm = None
demands = None
home = None
capacity = None
cm = None

def evaluate_distance(self):
    """A simple objective function to calculate distances
    for the VRP problem.

    Returns:
        int: the total distance of the path
    """

    fitness = 0
    routes = split_to_routes(self)

    for route in routes:
        route = [home] + route + [home]
        for i in range(1,len(route)):
            # Calculates full distance, including from last city
            # to first, to terminate the trip
            pos_from = route[i - 1]
            pos_to = route[i]
            distance = dm[pos_from][pos_to]
            fitness += distance

    return int(fitness)

def evaluate_co2(self):
    fitness = 0
    routes = split_to_routes(self)

    for route in routes:
        route = [home] + route + [home]
        for i in range(1,len(route)):
            # Calculates full distance, including from last city
            # to first, to terminate the trip
            pos_from = route[i - 1]
            pos_to = route[i]
            distance = cm[pos_from][pos_to]
            fitness += distance

    return int(fitness)
    


def split_to_routes(self):
    routes = []
    routes_cap = []
    route = []
    route_cap = 0
    for i in range(len(self.representation)):
        pos = self.representation[i]
        pos_demand = demands[pos]
        if route_cap + pos_demand > capacity:
            routes.append(route)
            routes_cap.append(route_cap)
            route = []
            route_cap = 0
        route_cap += pos_demand
        route.append(pos)

    routes.append(route)
    routes_cap.append(route_cap)

    return routes

# from TSP
def get_neighbours(self):
    """A neighbourhood function for the TSP problem. Switches
    indexes around in pairs.

    Returns:
        list: a list of individuals
    """
    n = [deepcopy(self.representation) for i in range(len(self.representation) - 1)]

    for count, i in enumerate(n):
        i[count], i[count + 1] = i[count + 1], i[count]

    n = [Individual(i) for i in n]
    return n


if __name__ == '__main__':
    # Monkey patching
    Individual.evaluate = evaluate_distance
    Individual.evaluate2 = evaluate_co2
    Individual.get_neighbours = get_neighbours

    dm = nodes.dist_matrix
    cm = nodes.co2_matrix
    demands = nodes.weights
    home = 0
    capacity = nodes.capacity
    mut.dm = nodes.dist_matrix
    mut.home = 0
    co.dm = nodes.dist_matrix
    co.home = 0
    sel.mo_functions = [evaluate_distance, evaluate_co2]


    def run():
        # Monkey patching
        Individual.evaluate = evaluate_distance
        #Individual.evaluate2 = evaluate_co2
        Individual.get_neighbours = get_neighbours

        dm = nodes.dist_matrix
        cm = nodes.co2_matrix
        demands = nodes.weights
        home = 0
        capacity = nodes.capacity
        mut.dm = nodes.dist_matrix
        mut.home = 0
        co.dm = nodes.dist_matrix
        co.home = 0
        sel.mo_functions = [evaluate_distance, evaluate_co2]

        pop = Population(
            size=80,
            sol_size=len(dm[0]),
            valid_set=[i for i in range(len(dm[0]))],
            replacement=False,
            optim="min",
        )

        pop.evolve(

            gens=2000, 
            select= rank,
            crossover= ordered_co,
            mutate=swap_mutation,
            co_p=0.9,
            mu_p=0.05,
            elitism=True,
            print_all_pareto=False,
            prem = False,
            log_only_last=True
        )

    N = 48
    time1 = time.time()
    Parallel(n_jobs=3)(delayed(run)() for i in range(N))
    print(time.time() - time1)

