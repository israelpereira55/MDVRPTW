import math
import numpy as np
from copy import deepcopy

from vrp import VRPTW, solomon, common

class MDVRPTW_Solution:   
    #mdvrptw
    #vrptw_solutions
    #vrptw_subproblems
    #clustered_clients


    def __init__(self, mdvrptw, clustered_clients):
        self.vrptw_solutions = []
        self.vrptw_subproblems = []
        self.clustered_clients = deepcopy(clustered_clients)

        for i in range(mdvrptw.number_of_depots):
            vrptw = VRPTW(number_of_vertices = len(self.clustered_clients[i]))
            vrptw.create_by_cluster(vrptw_index=i, cluster=self.clustered_clients[i], depot=mdvrptw.depots[i], mdvrptw=mdvrptw)
            self.vrptw_subproblems.append(vrptw)

        self.mdvrptw = mdvrptw


    def construct_solution_with_solomon(self, alpha1, alpha2, mu, lambdaa):
        vrptw_solutions = []
        for vrptw_subproblem in self.vrptw_subproblems:
            vrptw_solution = solomon.insertion_heuristic(vrptw_subproblem, alpha1, alpha2, mu, lambdaa)
            vrptw_solutions.append(vrptw_solution)

        self.vrptw_solutions = vrptw_solutions

    #def check_viability(self):
    #    if 

    def get_travel_distance(self):
        mdvrptw_cost = 0
        for vrptw_solution in self.vrptw_solutions:
            mdvrptw_cost += vrptw_solution.travel_distance

        return mdvrptw_cost

    def recalculate_travel_distance(self):
        mdvrptw_cost = 0
        for vrptw_solution in self.vrptw_solutions:
            mdvrptw_cost += vrptw_solution.calculate_cost()

        return mdvrptw_cost


    def print_solution(self):
        infeasible = False
        mdvrptw_route_distances = 0

        print("\n-------------------------------------- SOLUTION -------------------------------------------")
        for index in range(self.mdvrptw.number_of_depots):
            vrptw_route_distances = 0
            cluster = self.clustered_clients[index]
            vrptw_solution = self.vrptw_solutions[index]
            vrptw_subproblem = self.vrptw_subproblems[index]

            print(f"==> VRPTW SUBPROBLEM #{index}",
                   "\nCLUSTER:", cluster)
            
            print("\n--> SOLUTION:")
            for route_index, route in enumerate(vrptw_solution.routes):
                route_distance = 0

                ci_vrptw = route[0]
                string_route_vrptw = str(ci_vrptw)

                ci_mdvrptw = cluster[route[0]]
                string_route_mdvrptw = str(ci_mdvrptw)

                for j in range(1, len(route)):
                    cj_vrptw = route[j]
                    cj_mdvrptw = cluster[route[j]]

                    string_route_vrptw += " - " + str(cj_vrptw)
                    string_route_mdvrptw += " - " + str(cj_mdvrptw)
                    route_distance += vrptw_subproblem.distances[ci_vrptw][cj_vrptw]

                    ci_vrptw = cj_vrptw

                print(f"Route #{route_index +1}:\n" +
                      string_route_vrptw + 
                      f"\nReal route #{route_index}:\n" +
                      string_route_mdvrptw)

                vrptw_route_distances += route_distance
                print("Travelled distance: {}, Demand: {}, Free: {}".format(round(route_distance,2), vrptw_subproblem.vehicle_capacity - vrptw_solution.free_capacities[route_index], vrptw_solution.free_capacities[route_index]))
                print("")


            if len(vrptw_solution.routes) > vrptw_subproblem.number_of_vehicles:
                infeasible = True

            mdvrptw_route_distances += vrptw_route_distances
            print(f"--> Disponible vehicles {vrptw_subproblem.number_of_vehicles}. Used vehicles {len(vrptw_solution.routes)}\n" +
                  f"==> VRPTW travelled distance: {round(vrptw_route_distances,2)}\n\n")
            index +=1


        if infeasible:
            print("Feasble: NO")
        else:
            print("Feasible: YES")

        print("==> MDVRPTW Total travelled distance:", round(mdvrptw_route_distances,2))
        print("-------------------------------------------------------------------------------------------")


    def print_conversion(self, vrptw_index):

        print("\n-------------------------------------------------------------------------------------------")
        print("VRPTW -> MDVRPTW")
        for i, ci in enumerate(self.clustered_clients[vrptw_index]):
            print(f'{i} -> {ci}')
        print("-------------------------------------------------------------------------------------------")


    def is_feasible(self, print_route=False):
        for vrptw_solution in self.vrptw_solutions:
            if not vrptw_solution.is_feasible(vrptw_solution.vrptw.depot, print_route):
                return False
        return True

    def is_feasible_by_number_of_vehicles(self):
        for vrptw_solution in self.vrptw_solutions:
            if len(vrptw_solution.routes) > vrptw_solution.vrptw.depot.number_of_vehicles:
                return False
        return True

    def is_feasible_by_time_windows(self):
        for vrptw_solution in self.vrptw_solutions:
            for route in vrptw_solution.routes:
                if not common.is_feasible_by_time_windows(route, vrptw_solution.vrptw):
                    return False
        return True

    def is_feasible_by_demand(self):
        for vrptw_solution in self.vrptw_solutions:
            if not vrptw_solution.is_feasible_by_demand(vrptw_solution.vrptw.depot):
                return False
        return True

    def check_clients_solution(self):
        clients = np.zeros((self.mdvrptw.number_of_clients+1))
        n = 0
        for depot_index, vrptw_solution in enumerate(self.vrptw_solutions):
            for route in vrptw_solution.routes:
                if route[0] != 0 or route[-1] != 0:
                    print("check the route depot:", route)
                    exit(1) 

                for i in range(1,len(route)-1):
                    ci_vrptw = route[i]
                    ci_mdvrptw = self.get_client_id_mdvrptw(depot_index, ci_vrptw)

                    if clients[ci_mdvrptw] == 1:
                        print(f"Client {ci_mdvrptw} routered twice")
                        exit(1)
                    
                    clients[ci_mdvrptw] = 1
                    n += 1

        if n != self.mdvrptw.number_of_clients:
            print("Missing client.")
            exit(1)

    def check_demand(self):
        for vrptw_solution in self.vrptw_solutions:
            vrptw_solution.check_demand()


    def get_client_id_vrptw(self, depot_index, ci_mdvrptw): #TODO REMOVE N USE ON COMMON
        for i, ci_vrptw in enumerate(self.clustered_clients[depot_index]):
            if ci_vrptw == ci_mdvrptw:
                return i

        return None

    def get_client_id_mdvrptw(self, depot_index, ci_vrptw):
        return self.clustered_clients[depot_index][ci_vrptw]


