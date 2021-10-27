import numpy as np
from matplotlib import pyplot

from vrp import common

# Just used to react like a goto on 2-opt
class GotImprovementException(Exception):
    pass


def two_opt_vrptw_hibrid_first_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    vrptw_solution.print_solution()
    #vrptw_solution.travel_distance = vrptw_solution.calculate_cost()

    start_route, start_i, start_j = 0,1,2

    got_improvement = True
    while got_improvement:
        got_improvement = False

        try: 
            cost = vrptw_solution.travel_distance
            for routei_index in range(start_route, len(vrptw_solution.routes)): 
            #for routei_index,routei in enumerate(vrptw_solution.routes): 

                routei = vrptw_solution.routes[routei_index] #enumerate nao é tao bom pq tem q atualizar
                for i in range(start_i, len(routei)-1): # (-2) take out depot on first and last position
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
                            
                            #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                #Calculating new travel distance
                                if i == j-1:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                                           - vrptw.distances[cj][c_j_plus1] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                                           + vrptw.distances[ci][c_j_plus1]

                                    # TODO, remove vrptw.distances[ci][cj] from above
                                else:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                           - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                           + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

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
                                vrptw_solution.swap_two_cities(i, routei_index, j, routej_index)
                                cost = new_cost
                                #updated_solution = True

                                if i == len(routei)-1: # Defining the start point of the algorithm rerun.
                                    start_route, start_i = routei_index+1, 1
                                else:
                                    start_route, start_i = routei_index, i+1

                                #got_improvement = True
                                raise GotImprovementException

                    #print('-')

                start_i = 1
        except GotImprovementException:
            got_improvement = True

def two_opt_vrptw_hibrid_best_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    vrptw_solution.print_solution()
    #vrptw_solution.travel_distance = vrptw_solution.calculate_cost()

    start_routei, start_i, start_routej, start_j = 0,1, 0,2

    got_improvement = True
    updated_solution = False
    while got_improvement:
        got_improvement = False

        try: 
            cost = vrptw_solution.travel_distance
            for routei_index in range(start_routei, len(vrptw_solution.routes)): 
            #for routei_index,routei in enumerate(vrptw_solution.routes): 

                routei = vrptw_solution.routes[routei_index] #enumerate nao é tao bom pq tem q atualizar
                for i in range(start_i, len(routei)-1): # (-2) take out depot on first and last position
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
                            
                            #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                #Calculating new travel distance
                                if i == j-1:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                                           - vrptw.distances[cj][c_j_plus1] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                                           + vrptw.distances[ci][c_j_plus1]

                                    # TODO, remove vrptw.distances[ci][cj] from above
                                else:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                           - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                           + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

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
                                vrptw_solution.swap_two_cities(i, routei_index, j, routej_index)
                                cost = new_cost

                                # Defining the start point of the algorithm rerun.
                                start_routei, start_i = routei_index, i

                                #got_improvement = True
                                raise GotImprovementException

                    #print('-')

                start_i = 1
        except GotImprovementException:
            got_improvement = True
    return


def two_opt_vrptw_best_improvement_old(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    vrptw_solution.print_solution()
    #vrptw_solution.travel_distance = vrptw_solution.calculate_cost()

    start_routei, start_i, start_routej, start_j = 0,1, 0,2

    updated_solution = False
    got_improvement = True
    while got_improvement:
        got_improvement = False

        try: 
            cost = vrptw_solution.travel_distance
            for routei_index in range(start_routei, len(vrptw_solution.routes)): 
            #for routei_index,routei in enumerate(vrptw_solution.routes): 

                routei = vrptw_solution.routes[routei_index] #enumerate nao é tao bom pq tem q atualizar
                for i in range(start_i, len(routei)-1): # (-2) take out depot on first and last position
                    ci = routei[i]
                    c_i_less1 = routei[i-1]
                    c_i_plus1 = routei[i+1]

                    if not updated_solution:
                        start_routej = routei_index

                    for routej_index in range(start_routej, len(vrptw_solution.routes)):
                        routej = vrptw_solution.routes[routej_index]
                        
                        if updated_solution:
                            start = start_j 
                        else:
                            start = i+1 if routei_index == routej_index else 1 #if the same route, then go i+1, else get the first client of a route
                        updated_solution = False

                        for j in range(start, len(vrptw_solution.routes[routej_index])-1):
                            cj = routej[j]
                            c_j_less1 = routej[j-1]
                            c_j_plus1 = routej[j+1]
                            
                            print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                #Calculating new travel distance
                                if i == j-1:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                                           - vrptw.distances[cj][c_j_plus1] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                                           + vrptw.distances[ci][c_j_plus1]

                                    # TODO, remove vrptw.distances[ci][cj] from above
                                else:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                           - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                           + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

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
                                vrptw_solution.swap_two_cities(i, routei_index, j, routej_index)
                                cost = new_cost
                                #updated_solution = True

                                # Defining the start point of the algorithm rerun.

                                updated_solution= True
                                start_routei, start_i = routei_index, i
                                if j == len(routej)-1:
                                    start_routej, j = routej_index +1, 1
                                else:
                                    start_routej, j = routej_index, j+1


                                print("melhorei!!!")
                                vrptw_solution.print_solution()
                                print("")

                                #got_improvement = True
                                raise GotImprovementException

                    print('-')

                start_i = 1
        except GotImprovementException:
            got_improvement = True

def two_opt_vrptw_first_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    #vrptw_solution.print_solution()

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
                            
                            #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                #Calculating new travel distance
                                if i == j-1:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                                           - vrptw.distances[cj][c_j_plus1] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                                           + vrptw.distances[ci][c_j_plus1]

                                    # TODO, remove vrptw.distances[ci][cj] from above
                                else:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                           - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                           + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

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
                                vrptw_solution.swap_two_cities(i, routei_index, j, routej_index)
                                cost = new_cost
                                raise GotImprovementException

                    #print('-')
        except GotImprovementException:
            got_improvement = True


def two_opt_vrptw_best_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    #vrptw_solution.print_solution()
    best_pj = -1,-1

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
                            
                            #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

                            #Checking Time Windows
                            if routei_index == routej_index:
                                if not common.is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue

                                #Calculating new travel distance
                                if i == j-1:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                                           - vrptw.distances[cj][c_j_plus1] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                                           + vrptw.distances[ci][c_j_plus1]

                                    # TODO, remove vrptw.distances[ci][cj] from above
                                else:
                                    new_cost = cost \
                                           - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                           + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                           - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                           + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

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
                                cost = new_cost
                                best_pj = routej_index, j
                                got_improvement = True

                    if got_improvement:
                        routej_indexj, jj = best_pj
                        vrptw_solution.swap_two_cities(i, routei_index, jj, routej_indexj)

                        raise GotImprovementException

                    #print('-')
        except GotImprovementException:
            pass


def two_opt_mdvrptw(mdvrptw_solution):

    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_opt_vrptw_first_improvement(vrptw_solution)

    return mdvrptw_solution

