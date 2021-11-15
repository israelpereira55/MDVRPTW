import numpy as np
from matplotlib import pyplot

from vrp import common, plot

# Just used to react like a goto on 2-swap
class GotImprovementException(Exception):
    pass


def two_swap_vrptw_hibrid_first_improvement(vrptw_solution):
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

def two_swap_vrptw_hibrid_best_improvement(vrptw_solution):
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


def two_swap_vrptw_best_improvement_old(vrptw_solution):
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

def two_swap_vrptw_first_improvement(vrptw_solution):
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


def two_swap_vrptw_best_improvement(vrptw_solution):
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


def two_swap_mdvrptw(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_swap_vrptw_first_improvement(vrptw_solution)

    return mdvrptw_solution


def drop_one_point_intra_depot_vrptw(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

    #vrptw_solution.print_solution()
    best_pj = -1,-1
    got_improvement = False
    for routei_index in range(len(vrptw_solution.routes)): 
    #for routei_index,routei in enumerate(vrptw_solution.routes): 
        cost = vrptw_solution.travel_distance
        routei = vrptw_solution.routes[routei_index] #enumerate nao é tao bom pq tem q atualizar
        #for i in range(1, len(routei)-1): # (-2) take out depot on first and last position
        i = 1
        while i < len(routei)-1:
            ci = routei[i]
            c_i_less1 = routei[i-1]
            c_i_plus1 = routei[i+1]

            for routej_index in range(routei_index+1, len(vrptw_solution.routes)):
                routej = vrptw_solution.routes[routej_index]
                
                for j in range(1, len(vrptw_solution.routes[routej_index])-1):
                    cj = routej[j]
                    c_j_less1 = routej[j-1]
                    #c_j_plus1 = routej[j+1] #after inserting ci, cj become the new cj+1

                    #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")
                    if not common.is_insertion_viable_by_demand(vrptw_solution, ci, routej_index):
                        continue                        

                    if not common.is_insertion_viable_by_time_windows(vrptw_solution, ci, j, routej_index):
                        continue

                    new_cost = cost \
                               - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                               + vrptw.distances[c_i_less1][c_i_plus1] \
                               \
                               + vrptw.distances[c_j_less1][ci] + vrptw.distances[cj][ci] \
                               - vrptw.distances[c_j_less1][cj]

                    if new_cost < cost:
                        cost = new_cost
                        best_pj = routej_index, j
                        got_improvement = True


            if got_improvement:
                best_route_index, best_index = best_pj
                vrptw_solution.remove_client(i, routei_index)
                vrptw_solution.insert_client(ci, best_index, best_route_index)
                got_improvement = False

                '''
                if round(vrptw_solution.travel_distance,2) != round(vrptw_solution.calculate_cost(), 2):
                    print(vrptw_solution.travel_distance, vrptw_solution.calculate_cost())
                    print("deu ruim")
                    exit(1)
                '''
            i+=1
            #print('-')



def drop_one_point_intra_depot_mdvrptw(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        drop_one_point_intra_depot_vrptw(vrptw_solution)

    return mdvrptw_solution


#TODO: more efficient with numpy vectors.
def drop_one_point_inter_depot_mdvrptw(mdvrptw_solution):
    mdvrptw = mdvrptw_solution.mdvrptw

    #Defining the 'clients_current_depot', which tells for each client, the depot it's related to.
    clients_current_depot = [-1] * (mdvrptw.number_of_clients+1)
    for cluster in mdvrptw_solution.clustered_clients:
        depot_index = cluster[0]
        for i in range(1, len(cluster)):
            client = cluster[i]
            clients_current_depot[client] = depot_index
                
    global_demands = []
    max_demands = []
    for vrptw_subproblem in mdvrptw_solution.vrptw_subproblems:
        global_demands.append(vrptw_subproblem.global_demand)
        max_demands.append(vrptw_subproblem.vehicle_capacity * vrptw_subproblem.number_of_vehicles)

    clients_closest_depot = []
    #for _ in range(mdvrptw.number_of_clients):
    #    clients_closest_depot.append([])

    #for ci in range(1, mdvrptw.number_of_clients+1):
    #    depot_distances = 
    #    for depot in mdvrptw.depots:
    #        if 

    '''
    client_depots = [-1] * mdvrptw.number_of_clients
    for ci in range(1, mdvrptw.number_of_clients+1):
        print(ci, mdvrptw.number_of_clients)
    '''
    print(clients_current_depot)
    exit(1)


# 2opt-intra
# credits: https://stackoverflow.com/questions/53275314/2-opt-algorithm-to-solve-the-travelling-salesman-problem-in-python
# Sadly Fradge didn't receive the best answer, but should!
#
# Edges
#   Before swap: c1-c2, c3-c4 
#   After swap:  c1-c3, c2-c4
def cost_swap(distances, c1, c2, c3, c4):
    return distances[c1][c3] + distances[c2][c4] - distances[c1][c2] - distances[c3][c4]

def two_opt_intra_route_old(vrptw_solution, route_index, steepest_descent=True):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    distances = vrptw.distances
    best = route
    #print("Started", route)

    got_improvement = True
    while got_improvement:
        #print("Start of 2opt")
        got_improvement = False

        try:
            #Disclaimer: as my routes are [0, 1, ..., n, 0], I have removed the last element on the iteration
            # If your case is like [0,1,...,n], it should be i=1 to len(route)-2; j=i+2 to len(route)
            for i in range(1, len(route)-3):
                for j in range(i+2, len(route) -1):
                    cost_update = cost_swap(distances, best[i-1], best[i], best[j-1], best[j])
                    if cost_update < 0:

                        new_route = best[:]
                        new_route[i:j] = best[j-1:i-1:-1]
                        if not common.is_feasible_by_time_windows(new_route, vrptw): #TODO, define start to save time
                            continue

                        best = new_route
                        vrptw_solution.travel_distance += cost_update
                        got_improvement = True
                        #print("improved", best)

                        if steepest_descent: 
                            raise GotImprovementException

                #if not steepest_descent and got_improvement:
                #    #coisa aqui
                #    pass

            route = best
        except GotImprovementException:
            pass
        #exit(1)

    #print("Last", route)
    return best

def get_cost(route, distances):
    sum_dist=0
    ci = route[0]
    for j in range(1, len(route)):
        cj = route[j]
        sum_dist+= distances[ci][cj]

    return sum_dist



def two_opt_intra_route(vrptw_solution, route_index, steepest_descent=True):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    distances = vrptw.distances
    best = route

    cost = get_cost(route, vrptw.distances)

    got_improvement = True
    while got_improvement:
        got_improvement = False

        try:
            #Disclaimer: as my routes are [0, 1, ..., n, 0], I have removed the last element on the iteration
            # If your case is like [0,1,...,n], it should be i=1 to len(route)-2; j=i+2 to len(route)
            for i in range(1, len(route)-3):
                for j in range(i+2, len(route) -1):
                        new_route = best[:]
                        new_route[i:j] = best[j-1:i-1:-1]

                        new_cost = get_cost(new_route, vrptw.distances)
                        if new_cost < cost:
                            if not common.is_feasible_by_time_windows(new_route, vrptw): #TODO, define start to save time
                                continue

                            cost = new_cost
                            best = new_route
                            vrptw_solution.travel_distance = vrptw_solution.travel_distance - (cost - new_cost)
                            got_improvement = True

                            if steepest_descent: 
                                raise GotImprovementException

                #if not steepest_descent and got_improvement:
                #    #coisa aqui
                #    pass

            route = best
        except GotImprovementException:
            pass

    return best

def two_opt_intra_route_hibrid(route, distances):
    got_improvement = True
    while got_improvement:
        got_improvement = False

        #Disclaimer: as my routes are [0, 1, ..., n, 0], I have removed the last element on the iteration
        # If your case is like [0,1,...,n], it should be i=1 to len(route)-2; j=i+2 to len(route)
        for i in range(1, len(route)-3):
            for j in range(i+2, len(route) -1):
                if cost_swap(distances, route[i-1], route[i], route[j-1], route[j]) < 0:
                    route[i:j] = route[j-1:i-1:-1]
                    got_improvement = True

    return route

def two_opt_intra_route_mdvrptw(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        for route_index in range(len(vrptw_solution.routes)):
            #cost = vrptw_solution.travel_distance
            two_opt_intra_route(vrptw_solution, route_index, steepest_descent=True)

            '''
            if vrptw_solution.travel_distance < cost:
                mdvrptw_solution.print_solution()
                print(mdvrptw_solution.get_travel_distance())
                plot.plot_mdvrptw_solution(mdvrptw_solution)
            '''


def local_search(mdvrptw_solution, print_solution=False):
    got_improvement = True
    while got_improvement:
        got_improvement= False
        cost = mdvrptw_solution.get_travel_distance()


        two_opt_intra_route_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)


        two_swap_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)

        
        drop_one_point_intra_depot_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)


        if mdvrptw_solution.get_travel_distance() < cost:
            got_improvement= True 

