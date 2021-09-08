import numpy as np
from matplotlib import pyplot

from vrp import common

# Just used to react like a goto on 2-opt
class GotImprovementException(Exception):
    pass


def two_opt_vrptw(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    got_improvement = True
    while got_improvement:
        got_improvement = False

        try: 
            cost = vrptw_solution.travel_distance
            for routei_index in range(len(vrptw_solution.routes)): 
            #for routei_index,routei in enumerate(vrptw_solution.routes): 

                routei = vrptw_solution.routes[routei_index] #enumerate nao é tao bom pq tem q atualizar
                for i in range(1, len(routei)-1): # (-2) take out depot on first and last position
                    ci = routei[i]
                    c_i_less1 = routei[i-1]
                    c_i_plus1 = routei[i+1]

                    for routej_index in range(routei_index, len(vrptw_solution.routes)):
                        routej = vrptw_solution.routes[routej_index]
                        
                        start = i+1 if routei_index == routej_index else 1 #if the same route, then go i+1, else get the first client of a route
                        for j in range(start, len(vrptw_solution.routes[routej_index])-1):
                            cj = routej[j]
                            c_j_less1 = routej[j-1]
                            c_j_plus1 = routej[j+1]
                            #print(ci, cj, i, j)

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                # If they are on the same route, there is no need to check demand feasibility.
                            else:
                                if not common.is_insertion_swap_viable_by_time_windows(vrptw_solution, ci, routei_index, j, routej_index) or \
                                   not common.is_insertion_swap_viable_by_time_windows(vrptw_solution, cj, routej_index, i, routei_index):
                                    continue

                                #Checking Demand
                                if not common.is_swap_viable_by_demand(vrptw_solution, ci, routei_index, cj, routej_index):
                                    continue

                            #Calc new cost
                            new_cost = cost \
                                       - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                       + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                       - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                       + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

                            if new_cost < cost:
                                vrptw_solution.routes[routei_index][i] = cj
                                vrptw_solution.routes[routej_index][j] = ci # TODO: swap em funcao pra mudar mais coisa
                                #TODO: em funcao tem que corrigir free capacities
                                cost = new_cost

                                vrptw_solution.travel_distance = cost

                                #got_improvement = True
                                vrptw_solution.print_solution()

                                raise GotImprovementException

                    #print('-')
        except GotImprovementException:
            got_improvement = True


def two_opt_mdvrptw(mdvrptw_solution):

    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
         two_opt_vrptw(vrptw_solution)

    return mdvrptw_solution

