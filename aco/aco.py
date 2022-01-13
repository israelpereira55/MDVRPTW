import math, random
import numpy as np

from vrp import local_search, common, VRPTW_Solution, MDVRPTW_Solution
from aco import Ant

class ACO:
    #ants : List
    #pheromones    [x,y]   

    m : int        # A sum from demands of all routes.]
    max_iterations : int # but can also happen the stagnation behavior, where all ants makes the same tour. TODO: implement a way to see that.

    Q : float       # constant??? amount of pheromone to be deposited along a tour (article)
    q0 : float       # ACS probability parameter in [0,1]. The lowest q are, the highest is the probability to make a random move.
    ro : float      # evaporation rate < 1
    alpha : float   # if alpha = 0, the pheromones are not considered
    beta  : float   # importance of heuristic function (fitness value)
    tau0  : float   # initial value for pheromones

    number_of_vertices : int

    def __init__(self, number_of_vertices, aco_settings): 
        self.m = aco_settings.m
        self.Q = aco_settings.Q #AS
        self.q0 = aco_settings.q0 #ACS
        self.ro = aco_settings.ro
        self.alpha= aco_settings.alpha #AS
        self.beta = aco_settings.beta
        self.tau0 = aco_settings.tau0
        self.max_iterations = aco_settings.max_iterations
        self.number_of_vertices = number_of_vertices

        self.ants = []
        self.best_ant = None
        self.pheromones = np.full((number_of_vertices+1, number_of_vertices+1), self.tau0)


    def inject_initial_population(self, solutions):
        for solution in solutions:
            self.ants.append(Ant(solution))
        self.update_pheromones()

    def update_pheromones(self):
        for i in range(self.number_of_vertices): #remove depot?
            for j in range(self.number_of_vertices):
                if i == j: continue

                self.pheromones[i][j] = (1-self.ro)*self.pheromones[i][j]
                for ant in self.ants:
                     self.pheromones[i][j] += ant.adj_matrix[i][j]*(self.Q / ant.mdvrptw_solution.get_travel_distance())
        #print(self.pheromones)


    def _get_viable_clients_vrptw(self, ci_mdvrptw, bi, route_demand, visited_clients, mdvrptw, depot, cluster):
        viable_clients = []
        for j in range(1, len(cluster)):
        #for cj_mdvrptw in range(1, mdvrptw.number_of_clients):
            cj_mdvrptw = cluster[j]
            if visited_clients[cj_mdvrptw]: continue #ci is setted to visited already

            #Checking demand restriction
            if mdvrptw.demands[cj_mdvrptw] + route_demand <= depot.vehicle_capacity:
                #Checking time windows restriction
                #bj = common.calculate_starting_time(vrptw, ci, bi, cj)
                bj = common.calculate_starting_time_mdvrptw(mdvrptw, ci_mdvrptw, bi, cj_mdvrptw)

                if bj <= mdvrptw.time_windows[cj_mdvrptw][1]:
                    viable_clients.append((cj_mdvrptw,bj))

        return viable_clients

    # The aco_probabilities is a list with ci, bi, pij, where pij is the ACO probability.
    # The first and last item has a fake client -1, but a probability 0 or 100%.
    def _get_probabilities(self, ci_mdvrptw, viable_clients, mdvrptw):
        aco_probabilities = []
        denominator = 0
        for cl_mdvrptw, bl in viable_clients:
            nil = 1/mdvrptw.distances[ci_mdvrptw][cl_mdvrptw]
            denominator += math.pow(self.pheromones[ci_mdvrptw][cl_mdvrptw], self.alpha) * math.pow(nil, self.beta)
            if denominator == 0:
                print('pheromones zero')
                exit(1)

        for cj_mdvrptw, bj in viable_clients:
            nij = 1/mdvrptw.distances[ci_mdvrptw][cj_mdvrptw]
            pij = math.pow(self.pheromones[ci_mdvrptw][cj_mdvrptw], self.alpha) * math.pow(nij, self.beta) / denominator

            aco_probabilities.append((cj_mdvrptw,bj,pij))

        return aco_probabilities

    def _select_next_city(self, aco_probabilities):
        aco_probabilities.sort(key = lambda x: x[2], reverse=True) #decrescente "não crescente"
        p = random.uniform(0,1)

        pbase = 0.
        for i in range(len(aco_probabilities) -1):
            cj_mdvrptw, bj, pij = aco_probabilities[i]
            if p >= pbase and p <= pij:
                return cj_mdvrptw, bj

            pbase += pij

        cj_mdvrptw, bj, pij = aco_probabilities[-1]
        return cj_mdvrptw, bj

    #Ant System 1995
    def AS_construct_ant_vrptw(self, mdvrptw, vrptw, cluster, problem_index):
        depot = mdvrptw.depots[problem_index]
        #vrptw = mdvrptw.vrptw_subproblems[problem_index]
        vrptw_solution = VRPTW_Solution(vrptw)

        route = [cluster[0]]
        route_demand = 0
        number_of_clients = len(cluster)
        
        bi = 0
        visited_clients = np.zeros((mdvrptw.number_of_clients+1))

        i = 0
        for n in range(len(cluster) -1): #TODO check all
        #umber_of_clients=0
        #while number_of_clients < len(cluster)-1:
            ci_mdvrptw = route[i]
            i+=1

            #ci_mdvrptw = cluster[ci_vrptw]
            if ci_mdvrptw <= mdvrptw.number_of_clients:#else, depot
                visited_clients[ci_mdvrptw] = 1
            
            viable_clients = self._get_viable_clients_vrptw(ci_mdvrptw, bi, route_demand, visited_clients, mdvrptw, depot, cluster)
            if len(viable_clients) > 0:
                aco_probabilities = self._get_probabilities(ci_mdvrptw, viable_clients, mdvrptw)
                cj_mdvrptw,bj = self._select_next_city(aco_probabilities)
                route.append(cj_mdvrptw)
                bi = bj

            else: #TODO: If it is higher than the number of vehicles, discart
                route.append(cluster[0])
                #print(cluster)
                #print(route)
                common.convert_route_to_vrptw(route, cluster) #TODO: find a more efficient way to do so. A vector to link the values is O(1), but is it necessary?
                #print(route)
                #exit(1)
                vrptw_solution.insert_route(route)

                
                bi = 0
                route = [cluster[0]]
                route_demand = 0

                viable_clients = self._get_viable_clients_vrptw(ci_mdvrptw, bi, route_demand, visited_clients, mdvrptw, depot, cluster)
                aco_probabilities = self._get_probabilities(ci_mdvrptw, viable_clients, mdvrptw)
                cj_mdvrptw,bj = self._select_next_city(aco_probabilities)
                route.append(cj_mdvrptw)

                #visited_clients[cj_mdvrptw] = 1
                bi = bj
                i = 1

            #number_of_clients += 1
            #print(number_of_clients)

        route.append(cluster[0])
        common.convert_route_to_vrptw(route, cluster) #TODO: find a more efficient way to do so. A vector to link the values is O(1), but is it necessary?
        vrptw_solution.insert_route(route)

        vrptw_solution.travel_distance = vrptw_solution.calculate_cost()
        return vrptw_solution

    def _ACS_local_update_pheromones(self, ant):
        for index, vrptw_solution in enumerate(ant.mdvrptw_solution.vrptw_solutions):
            cluster = ant.mdvrptw_solution.clustered_clients[index]
            for route in vrptw_solution.routes:
                ci = cluster[route[0]]
                for j in range(1, len(route)):
                    cj = cluster[route[j]]

                    self.pheromones[ci][cj] = (1-self.ro) * self.pheromones[ci][cj] + self.ro*self.tau0

    def _ACS_global_update_pheromones(self, best_ant):
        ant = best_ant #TODO: rename on all code on function
        distance = ant.mdvrptw_solution.get_travel_distance()
        for index, vrptw_solution in enumerate(ant.mdvrptw_solution.vrptw_solutions):
            cluster = ant.mdvrptw_solution.clustered_clients[index]
            for route in vrptw_solution.routes:
                ci = cluster[route[0]]
                for j in range(1, len(route)):
                    cj = cluster[route[j]]

                    self.pheromones[ci][cj] = (1-self.ro) * self.pheromones[ci][cj] + self.ro/distance


    def _ACS_get_probabilities(self, ci_mdvrptw, viable_clients, mdvrptw):
        aco_probabilities = []
        denominator = 0
        for cl_mdvrptw, bl in viable_clients:
            nil = 1/mdvrptw.distances[ci_mdvrptw][cl_mdvrptw]
            denominator += self.pheromones[ci_mdvrptw][cl_mdvrptw] * math.pow(nil, self.beta)
            if denominator == 0:
                print('pheromones zero')
                exit(1)

        for cj_mdvrptw, bj in viable_clients:
            nij = 1/mdvrptw.distances[ci_mdvrptw][cj_mdvrptw]
            pij = self.pheromones[ci_mdvrptw][cj_mdvrptw] * math.pow(nij, self.beta) / denominator

            aco_probabilities.append((cj_mdvrptw,bj,pij))

        return aco_probabilities

    def ACS_get_arg_max(self, ci, viable_clients, mdvrptw):
        args = np.zeros((len(viable_clients)))

        for i in range(len(viable_clients)):
            cj,bj = viable_clients[i]
            args[i] = self.pheromones[ci][cj] * math.pow(1/mdvrptw.distances[ci][cj], self.beta)

        argmax = np.argmax(args)
        cj,_ = viable_clients[argmax]
        return cj

    #Ant Colony System 1997
    def ACS_construct_ant_vrptw(self, mdvrptw, vrptw, cluster, problem_index):
        depot = mdvrptw.depots[problem_index]
        #vrptw = mdvrptw.vrptw_subproblems[problem_index]
        vrptw_solution = VRPTW_Solution(vrptw)

        route = [cluster[0]]
        route_demand = 0
        number_of_clients = len(cluster)
        
        bi = 0
        visited_clients = np.zeros((mdvrptw.number_of_clients+1))

        i = 0
        for n in range(len(cluster) -1): #TODO check all
        #umber_of_clients=0
        #while number_of_clients < len(cluster)-1:
            ci_mdvrptw = route[i]
            i+=1

            #ci_mdvrptw = cluster[ci_vrptw]
            if ci_mdvrptw <= mdvrptw.number_of_clients:#else, depot
                visited_clients[ci_mdvrptw] = 1
            
            q = random.uniform(0,1)
            viable_clients = self._get_viable_clients_vrptw(ci_mdvrptw, bi, route_demand, visited_clients, mdvrptw, depot, cluster)
            if len(viable_clients) > 0:
                if q <= self.q0:
                    cj_mdvrptw = self.ACS_get_arg_max(ci_mdvrptw, viable_clients, mdvrptw)
                    bj = common.calculate_starting_time_mdvrptw(mdvrptw, ci_mdvrptw, bi, cj_mdvrptw)
                else:
                    aco_probabilities = self._ACS_get_probabilities(ci_mdvrptw, viable_clients, mdvrptw)
                    cj_mdvrptw,bj = self._select_next_city(aco_probabilities)
                    
                route.append(cj_mdvrptw)
                bi = bj

            else: #TODO: If it is higher than the number of vehicles, discart
                route.append(cluster[0])
                common.convert_route_to_vrptw(route, cluster) #TODO: find a more efficient way to do so. A vector to link the values is O(1), but is it necessary?
                vrptw_solution.insert_route(route)

                
                bi = 0
                route = [cluster[0]]
                route_demand = 0

                viable_clients = self._get_viable_clients_vrptw(ci_mdvrptw, bi, route_demand, visited_clients, mdvrptw, depot, cluster)
                
                if q <= self.q0:
                    cj_mdvrptw = self.ACS_get_arg_max(ci_mdvrptw, viable_clients, mdvrptw)
                    bj = common.calculate_starting_time_mdvrptw(mdvrptw, ci_mdvrptw, bi, cj_mdvrptw)
                else:
                    aco_probabilities = self._ACS_get_probabilities(ci_mdvrptw, viable_clients, mdvrptw)
                    cj_mdvrptw,bj = self._select_next_city(aco_probabilities)

                #aco_probabilities = self._get_probabilities(ci_mdvrptw, viable_clients, mdvrptw)
                #cj_mdvrptw,bj = self._select_next_city(aco_probabilities)
                route.append(cj_mdvrptw)

                #visited_clients[cj_mdvrptw] = 1
                bi = bj
                i = 1

            #number_of_clients += 1
            #print(number_of_clients)

        route.append(cluster[0])
        common.convert_route_to_vrptw(route, cluster) #TODO: find a more efficient way to do so. A vector to link the values is O(1), but is it necessary?
        vrptw_solution.insert_route(route)

        vrptw_solution.travel_distance = vrptw_solution.calculate_cost()
        return vrptw_solution

    def construct_ant_mdvrptw(self, mdvrptw, clustered_clients):
        mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients) #TODO: reconstruct a MDVRPTW_SOLUTION without the need of recreating one

        for index, vrptw_subproblem in enumerate(mdvrptw_solution.vrptw_subproblems):
            vrptw_solution = self.AS_construct_ant_vrptw(mdvrptw, vrptw_subproblem, mdvrptw_solution.clustered_clients[index], problem_index=index)
            while not vrptw_solution.is_feasible(depot=mdvrptw_solution.mdvrptw.depots[index]):
                self.dissolve_pheromones_infeasible_vrptw(vrptw_solution, cluster=mdvrptw_solution.clustered_clients[index])
                vrptw_solution = self.AS_construct_ant_vrptw(mdvrptw, vrptw_subproblem, mdvrptw_solution.clustered_clients[index], problem_index=index)
                #print('infeasible vrptw')
                #print(self.pheromones)


            #print("feasible vrptw!")
            #print(self.pheromones)
            #exit(1)
            mdvrptw_solution.vrptw_solutions.append(vrptw_solution) 

        ant = Ant(mdvrptw_solution)
        #ant.mdvrptw_solution.print_solution()
        return ant

    def ACS_construct_ant_mdvrptw(self, mdvrptw, clustered_clients):
        mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients) #TODO: reconstruct a MDVRPTW_SOLUTION without the need of recreating one

        for index, vrptw_subproblem in enumerate(mdvrptw_solution.vrptw_subproblems):
            vrptw_solution = self.ACS_construct_ant_vrptw(mdvrptw, vrptw_subproblem, mdvrptw_solution.clustered_clients[index], problem_index=index)
            while not vrptw_solution.is_feasible(depot=mdvrptw_solution.mdvrptw.depots[index]):
                self.dissolve_pheromones_infeasible_vrptw(vrptw_solution, cluster=mdvrptw_solution.clustered_clients[index])
                vrptw_solution = self.ACS_construct_ant_vrptw(mdvrptw, vrptw_subproblem, mdvrptw_solution.clustered_clients[index], problem_index=index)
                print('infeasible vrptw')
                print(self.pheromones)


            #print("feasible vrptw!")
            #print(self.pheromones)
            #exit(1)
            mdvrptw_solution.vrptw_solutions.append(vrptw_solution) 

        ant = Ant(mdvrptw_solution)
        #ant.mdvrptw_solution.print_solution()
        return ant


    def run_AS(self, mdvrptw, clustered_clients, print_progress=True):
        best_cost = float('inf')

        for gi in range(self.max_iterations):
            new_generation = []
            for k in range(self.m):
                #construct ants
                ant = self.construct_ant_mdvrptw(mdvrptw, clustered_clients)

                ant.mdvrptw_solution.check_clients_solution()
                #if ant.mdvrptw_solution.is_feasible():
                #    print("feasible")
                    
                #else:
                #    print("infeasible")
                    #exit(1)

                #ant.mdvrptw_solution.print_solution()
                #exit(1)

                #local search
                local_search.local_search(ant.mdvrptw_solution)
                print("Ant cost:", ant.mdvrptw_solution.get_travel_distance())
                new_generation.append(ant)
                #print("ACO NEW GENERATION", gi)

                cost = ant.mdvrptw_solution.get_travel_distance()
                if cost < best_cost: #not necessary to round the cost 
                    self.best_ant = ant
                    best_cost = cost

                    if print_progress: print(f"[ACO]: Generation {gi}.\n       New best cost {cost}\n")

            self.ants = new_generation

            #update pheromones
            self.update_pheromones()

    def run_ACS(self, mdvrptw, clustered_clients, print_progress=True):
        best_cost = float('inf')

        for gi in range(self.max_iterations):
            new_generation = []
            for k in range(self.m):
                #construct ants
                ant = self.ACS_construct_ant_mdvrptw(mdvrptw, clustered_clients)
                self._ACS_local_update_pheromones(ant)

                ant.mdvrptw_solution.check_clients_solution()
                #if ant.mdvrptw_solution.is_feasible():
                #    print("feasible")
                    
                #else:
                #    print("infeasible")
                    #exit(1)

                #ant.mdvrptw_solution.print_solution()
                #exit(1)

                #local search
                local_search.local_search(ant.mdvrptw_solution)
                print("Ant cost:", ant.mdvrptw_solution.get_travel_distance())
                new_generation.append(ant)
                #print("ACO NEW GENERATION", gi)

                cost = ant.mdvrptw_solution.get_travel_distance()
                if cost < best_cost: #not necessary to round the cost 
                    self.best_ant = ant
                    best_cost = cost

                    if print_progress: print(f"[ACO]: Generation {gi}.\n       New best cost {cost}\n")

            self._ACS_global_update_pheromones(self.best_ant)
            self.ants = new_generation

            #update pheromones
            self.update_pheromones()
    
    def dissolve_pheromones_infeasible_ant(self, ant):
        print(self.pheromones)
        for index, vrptw_solution in enumerate(ant.mdvrptw_solution.vrptw_solutions):
            cluster = ant.mdvrptw_solution.clustered_clients[index]
            for route in vrptw_solution.routes:
                ci = route[cluster[0]]
                for j in range(1, len(route)):
                    cj = route[cluster[j]]
                    self.pheromones[ci][cj] = (1-self.ro)*self.pheromones[i][j]

        print(self.pheromones)

    def dissolve_pheromones_infeasible_vrptw(self, vrptw_solution, cluster):
        #print(self.pheromones)
        #self.print_pheromones()

        for route in vrptw_solution.routes:
            ci = cluster[route[0]]
            for j in range(1, len(route)):
                cj = cluster[route[j]]
                self.pheromones[ci][cj] = (1-self.ro)*self.pheromones[ci][cj]

        #self.print_pheromones()
        #exit(1)

    def print_pheromones(self):
        for i in range(len(self.pheromones)):
            for j in range(len(self.pheromones[i])):
                print(self.pheromones[i][j], end='')
            print('')