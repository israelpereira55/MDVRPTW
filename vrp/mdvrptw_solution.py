import numpy as np
import math

from vrp import VRPTW, solomon


class MDVRPTW_Solution:   
    #routes 
    #demands
    #routed_clients


    def __init__(self, mdvrptw, clustered_clients):
        self.mdvrptw = mdvrptw

        self.vrptw_solutions = []
        self.vrptw_subproblems = []
        self.clustered_clients = clustered_clients

        for i in range(self.mdvrptw.number_of_depots):
            vrptw_subproblem = VRPTW(number_of_vertices = len(self.clustered_clients[i]))
            vrptw_subproblem.create_by_cluster(vrptw_index=i, clustered_clients=self.clustered_clients[i], depot=self.mdvrptw.depots[i], mdvrptw=self.mdvrptw)
            self.vrptw_subproblems.append(vrptw_subproblem)



    def construct_solution_with_solomon(self, alpha1, alpha2, mu, lambdaa, debug=False, debug_level2=False):
        
        vrptw_solutions = []
        for vrptw_subproblem in self.vrptw_subproblems:
            vrptw_solution = solomon.insertion_heuristic(vrptw_subproblem, alpha1, alpha2, mu, lambdaa, debug, debug_level2)
            vrptw_solutions.append(vrptw_solution)

        self.vrptw_solutions = vrptw_solutions

    #def check_if_feasible(self):
    #    if 

    def print_solution(self):
        infeasible = False
        mdvrptw_route_distances = 0

        print("\n-------------------------------------- SOLUTION -------------------------------------------")
        for index in range(self.mdvrptw.number_of_depots):
            vrptw_route_distances = 0
            vrptw_solution = self.vrptw_solutions[index]
            vrptw_subproblem = self.vrptw_subproblems[index]

            print(f"==> VRPTW SUBPROBLEM #{index}",
                   "\nCLUSTER:", self.clustered_clients[index])
            
            print("\n--> SOLUTION:")
            for i in range(len(vrptw_solution.routes)):
                route_distance = 0
                route = vrptw_solution.routes[i]

                string_route_vrptw = str(route[0])
                string_route_mdvrptw = str(self.clustered_clients[index][route[0]])
                for j in range(1, len(route)):
                    string_route_vrptw += " - " + str(route[j])
                    string_route_mdvrptw += " - " + str(self.clustered_clients[index][route[j]])
                    route_distance += vrptw_subproblem.distances[j-1][j]

                print(f"Route #{i}:\n" +
                      string_route_vrptw + 
                      f"\nReal route #{i}:\n" +
                      string_route_mdvrptw)

                vrptw_route_distances += route_distance
                print("Travelled distance: {}, Demand: {}, Free: {}".format(round(route_distance,2), vrptw_subproblem.vehicle_capacity - vrptw_solution.free_capacities[i], vrptw_solution.free_capacities[i]))
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





