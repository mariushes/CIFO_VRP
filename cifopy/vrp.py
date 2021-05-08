from data.vrp_data import capacity, demands, distance_matrix, home
from charles.charles import Population, Individual
from charles.search import hill_climb, sim_annealing
from charles.selection import fps, tournament
from charles.mutation import swap_mutation, swap_sequence_mutation, cheapest_insertion_mutation
import charles.mutation as mut
from charles.crossover import cycle_co

def evaluate(self):
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
            distance = distance_matrix[pos_from][pos_to]
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
    Individual.evaluate = evaluate
    Individual.get_neighbours = get_neighbours
    mut.distance_matrix = distance_matrix
    mut.home = home


    pop = Population(
        size=100,
        sol_size=len(distance_matrix[0]),
        valid_set=[i for i in range(len(distance_matrix[0]))],
        replacement=False,
        optim="min",
    )

    pop.evolve(
        gens=100, 
        select= tournament,
        crossover= cycle_co,
        mutate=swap_sequence_mutation,
        co_p=0.7,
        mu_p=0.1,
        elitism=True
    )