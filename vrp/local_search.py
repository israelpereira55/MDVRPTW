import numpy as np
from matplotlib import pyplot

from vrp import common, plot

# Just used to react like a goto on 2-swap
class GotImprovementException(Exception):
    pass


def two_swap_vrptw_hibrid_first_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

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
                            
                            if round(new_cost,8) < round(cost,8):
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
                            
                            if round(new_cost,8) < round(cost,8):
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


def two_swap_vrptw_first_improvement(vrptw_solution):
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
                            
                            if round(new_cost,8) < round(cost,8):
                                vrptw_solution.swap_two_cities(i, routei_index, j, routej_index)
                                cost = new_cost
                                raise GotImprovementException

                    #print('-')
        except GotImprovementException:
            got_improvement = True


def two_swap_vrptw_best_improvement(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

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
                            
                            if round(new_cost,8) < round(cost,8):
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


def two_swap_mdvrptw_first_improvement(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_swap_vrptw_first_improvement(vrptw_solution)

    return mdvrptw_solution

def two_swap_mdvrptw_best_improvement(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_swap_vrptw_best_improvement(vrptw_solution)

    return mdvrptw_solution

def two_swap_mdvrptw_hibrid_best_improvement(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_swap_vrptw_hibrid_best_improvement(vrptw_solution)

    return mdvrptw_solution

def two_swap_mdvrptw_hibrid_first_improvement(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        two_swap_vrptw_hibrid_first_improvement(vrptw_solution)

    return mdvrptw_solution



def drop_one_point_intra_depot_vrptw(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    number_of_clients = vrptw_solution.number_of_vertices -1

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

                    if round(new_cost,8) < round(cost,8):
                        cost = new_cost
                        best_pj = routej_index, j
                        got_improvement = True


            if got_improvement:
                best_route_index, best_index = best_pj
                vrptw_solution.remove_client(i, routei_index)
                if len(vrptw_solution.routes[routei_index]) == 2:
                    vrptw_solution.routes.pop(routei_index)

                vrptw_solution.insert_client(ci, best_index, best_route_index)
                got_improvement = False

            i+=1
            #print('-')


def drop_one_point_intra_depot_mdvrptw(mdvrptw_solution):
    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
        drop_one_point_intra_depot_vrptw(vrptw_solution)

    return mdvrptw_solution

# Checks if removing ci from ci_current_depot will decrease the mdvrptw_solution cost
# by reinserting ci on ci_next_depot on the route and index which gives the highest enhancement.
def dop_inter_depot_check_insertion_improvement(mdvrptw_solution, ci, ci_current_di, ci_next_di):
    mdvrptw = mdvrptw_solution.mdvrptw

    ci_current_depot_index = ci_current_di - mdvrptw.number_of_clients -1
    ci_next_depot_index = ci_next_di - mdvrptw.number_of_clients -1

    vrptw_current = mdvrptw_solution.vrptw_subproblems[ci_current_depot_index]
    vrptw_next = mdvrptw_solution.vrptw_subproblems[ci_next_depot_index]

    #Calculating mdvrptw_solution cost by removing ci from ci_current_depot
    vrptw_solution_current = mdvrptw_solution.vrptw_solutions[ci_current_depot_index]
    ci_vrptw = mdvrptw_solution.get_client_id_vrptw(ci_current_depot_index, ci)
    i_current_depot = vrptw_solution_current.get_client_location(ci_vrptw)

    c_i_less1 = vrptw_solution_current.routes[ i_current_depot[0] ][ i_current_depot[1]-1 ]
    c_i_plus1 = vrptw_solution_current.routes[ i_current_depot[0] ][ i_current_depot[1]+1 ]

    c_i_less1_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=ci_current_depot_index, ci_vrptw=c_i_less1)
    c_i_plus1_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=ci_current_depot_index, ci_vrptw=c_i_plus1)

    mdvrptw_cost = mdvrptw_solution.get_travel_distance()
    mdvrptw_cost_without_ci = mdvrptw_cost \
                            - mdvrptw.distances[c_i_less1_mdvrptw][ci] - mdvrptw.distances[c_i_plus1_mdvrptw][ci] \
                            + mdvrptw.distances[c_i_less1_mdvrptw][c_i_plus1_mdvrptw]
                            #TODO: REMOVE GET TRAVEL DISTANCE AND WORK ONLY WITH THE COST REMOVAL AND ADDITION

    #Now we will check the new distances
    vrptw_solution_next = mdvrptw_solution.vrptw_solutions[ci_next_depot_index]

    best_pj = -1,-1
    got_improvement = False

    mdvrptw_new_cost = float('inf')
    mdvrptw_local_cost = mdvrptw_cost #Local means that is the mdvrptw that is seeing on the iterations inside for
    for route_index in range(len(vrptw_solution_next.routes)): 
    #for routei_index,routei in enumerate(vrptw_solution.routes): 
        route = vrptw_solution_next.routes[route_index] #enumerate nao é tao bom pq tem q atualizar
        for j in range(1, len(route)-1):
            #print(ci, cj, f"({i},{routei_index}) x ({j}, {routej_index})")

            #Checking demand
            if vrptw_solution_next.free_capacities[route_index] < mdvrptw.demands[ci]:
                continue

            #Checking TW:
            if not common.is_insertion_viable_by_time_windows_mdvrptw(mdvrptw_solution, ci_next_depot_index, ci, route_index, j):
                continue

            c_j_less1 = route[j-1]
            c_j_plus1 = route[j]

            c_j_less1_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=ci_next_depot_index, ci_vrptw=c_j_less1)
            c_j_plus1_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=ci_next_depot_index, ci_vrptw=c_j_plus1)

            mdvrptw_new_cost = mdvrptw_cost_without_ci \
                            + mdvrptw.distances[c_j_less1_mdvrptw][ci] + mdvrptw.distances[c_j_plus1_mdvrptw][ci] \
                            - mdvrptw.distances[c_j_less1_mdvrptw][c_j_plus1_mdvrptw]

            #TODO: check cost for dop intra, why is it updating inside for? does it makes sense?
            if round(mdvrptw_new_cost,8) < round(mdvrptw_local_cost,8):
                mdvrptw_local_cost = mdvrptw_new_cost
                best_pj = route_index, j
                got_improvement = True


    if mdvrptw_new_cost < mdvrptw_cost:
        return True, mdvrptw_new_cost, best_pj[0], best_pj[1]

    return False, False, False, False


def drop_one_point_next_depot_mdvrptw(mdvrptw_solution):
    mdvrptw = mdvrptw_solution.mdvrptw

    #Defining the 'clients_current_depot', which tells for each client, the closest depot customer id 
    # it's related to.
    clients_current_depot = np.full((mdvrptw.number_of_clients+1), -1, dtype='int')
    for cluster in mdvrptw_solution.clustered_clients:
        di = cluster[0]
        for i in range(1, len(cluster)):
            client = cluster[i]
            clients_current_depot[client] = di

                
    # Global demands tells for each depot, the sum of demands for all clients it's related to.
    # Max demands defines for each depot, the maximum amount of demand we can support.
    global_demands = []
    max_demands = []
    for vrptw_subproblem in mdvrptw_solution.vrptw_subproblems:
        global_demands.append(vrptw_subproblem.global_demand)
        max_demands.append(vrptw_subproblem.vehicle_capacity * vrptw_subproblem.number_of_vehicles)


    # For each client, we will get the closest depot which is not the depot that the client
    # is already routed.
    clients_closest_depot = np.zeros(( mdvrptw.number_of_clients+1), dtype=int)
    for ci in range(1, mdvrptw.number_of_clients +1):
        lowest_index = -1
        lowest_distance = float('inf')
        for di in range(mdvrptw.number_of_clients +1, mdvrptw.number_of_clients + mdvrptw.number_of_depots):
            #We want to find the closest depot which the client is not already routed.
            #So, we are skipping the client current depot
            if di == clients_current_depot[ci]:
                continue

            distance = mdvrptw.distances[ci][di]
            if distance < lowest_distance:
                lowest_distance = distance
                lowest_index = di

            clients_closest_depot[ci] = lowest_index


    # Removing the depot if the demand would surpass it.
    for ci in range(1, mdvrptw.number_of_clients+1):
        closest_di = clients_closest_depot[ci]
        closest_depot_index = closest_di - mdvrptw.number_of_clients -1

        if global_demands[closest_depot_index] + mdvrptw.demands[ci] > max_demands[closest_depot_index]:
            clients_closest_depot[ci] = -1


    #Now we can start checking the distances.
    #for ci in range(1, mdvrptw.number_of_clients+1):
        closest_di = clients_closest_depot[ci]
        if closest_di == -1:
            continue

        #closest_depot_index = closest_di - mdvrptw.number_of_clients
        #client_current_depot = clients_current_depot[ci]

        got_improvement, mdvrptw_new_cost, route_index, index = dop_inter_depot_check_insertion_improvement(
                                                                mdvrptw_solution, ci, clients_current_depot[ci], closest_di)

        #Performing the inter depot insertion
        if got_improvement:
            current_depot_index = clients_current_depot[ci] - mdvrptw.number_of_clients -1
            
            ci_vrptw = mdvrptw_solution.get_client_id_vrptw(depot_index=current_depot_index, ci_mdvrptw=ci)
            pi = mdvrptw_solution.vrptw_solutions[current_depot_index].get_client_location(ci_vrptw)

            mdvrptw_solution.vrptw_solutions[current_depot_index].remove_client_from_problem(city_vrptw=ci_vrptw, route_index=pi[0], u=pi[1])
            mdvrptw_solution.clustered_clients[current_depot_index].pop(ci_vrptw)
            if len(mdvrptw_solution.vrptw_solutions[current_depot_index].routes[pi[0]]) == 2:
                mdvrptw_solution.vrptw_solutions[current_depot_index].routes.pop(pi[0])

            ci_vrptw = len(mdvrptw_solution.clustered_clients[closest_depot_index])
            mdvrptw_solution.vrptw_solutions[closest_depot_index].add_client_to_problem(
                                ci, ci_vrptw, mdvrptw.coordinates[ci], mdvrptw.time_windows[ci], mdvrptw.services[ci], mdvrptw.demands[ci], route_index, index)
            mdvrptw_solution.clustered_clients[closest_depot_index].insert(ci_vrptw, ci)



# 2opt-intra
# credits: https://stackoverflow.com/questions/53275314/2-opt-algorithm-to-solve-the-travelling-salesman-problem-in-python
# Sadly Fradge didn't receive the best answer, but should!
#
# Edges
#   Before swap: c1-c2, c3-c4 
#   After swap:  c1-c3, c2-c4
def cost_swap(distances, c1, c2, c3, c4):
    return distances[c1][c3] + distances[c2][c4] - distances[c1][c2] - distances[c3][c4]

def get_cost(route, distances):
    sum_dist=0
    ci = route[0]
    for j in range(1, len(route)):
        cj = route[j]
        sum_dist+= distances[ci][cj]
        ci = cj

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
                        new_route = route[:]
                        new_route[i:j] = route[j-1:i-1:-1]

                        new_cost = get_cost(new_route, vrptw.distances) #TODO: do better with upper solution
                        if round(new_cost,8) < round(cost,8):
                            if not common.is_feasible_by_time_windows(new_route, vrptw): #TODO, define start to save time
                                continue

                            best = new_route
                            vrptw_solution.routes[route_index] = best
                            vrptw_solution.travel_distance = vrptw_solution.travel_distance - (cost - new_cost)

                            cost = new_cost
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
            two_opt_intra_route(vrptw_solution, route_index, steepest_descent=True)


def local_search_print(mdvrptw_solution, print_solution=False):
    got_improvement = True
    while got_improvement:
        got_improvement= False
        cost = mdvrptw_solution.get_travel_distance()

        two_swap_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)

        two_opt_intra_route_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)

        drop_one_point_next_depot_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)

        drop_one_point_intra_depot_mdvrptw(mdvrptw_solution)
        if print_solution and mdvrptw_solution.get_travel_distance() < cost:
            mdvrptw_solution.print_solution()
            plot.plot_mdvrptw_solution(mdvrptw_solution)

        if mdvrptw_solution.get_travel_distance() < cost:
            got_improvement= True 


def local_search(mdvrptw_solution):
    got_improvement = True
    while got_improvement:
        got_improvement= False
        cost = mdvrptw_solution.get_travel_distance()

        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("aqui0")
            exit(1)

        two_swap_mdvrptw_best_improvement(mdvrptw_solution)
        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("aqui1")
            exit(1)

        two_opt_intra_route_mdvrptw(mdvrptw_solution)
        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("aqui2")
            exit(1)

        drop_one_point_next_depot_mdvrptw(mdvrptw_solution)
        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("aqui3")
            exit(1)

        drop_one_point_intra_depot_mdvrptw(mdvrptw_solution)
        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("aqui4")
            exit(1)


        ''' TODO: REMOVE
        Temporary functions for test
        '''

        if round(mdvrptw_solution.get_travel_distance(), 2) != round(mdvrptw_solution.recalculate_travel_distance(), 2):
            print("bad")
            exit(1)

        if not mdvrptw_solution.is_feasible():
            print('bad2')
            exit(1)

        if round(mdvrptw_solution.get_travel_distance(),2) != round(mdvrptw_solution.recalculate_travel_distance(),2):
            print('bad3')
            exit(1)

        if mdvrptw_solution.get_travel_distance() < cost:
            got_improvement= True 



def vnd(mdvrptw_solution):

    got_improvement = True
    while got_improvement:
        got_improvement= False
        cost = mdvrptw_solution.get_travel_distance()

        while True:
            two_swap_mdvrptw_best_improvement(mdvrptw_solution)
            if round(mdvrptw_solution.get_travel_distance(),8) < round(cost,8):
                got_improvement= True
                break

            two_opt_intra_route_mdvrptw(mdvrptw_solution)
            if round(mdvrptw_solution.get_travel_distance(),8) < round(cost,8):
                got_improvement= True
                break

            drop_one_point_next_depot_mdvrptw(mdvrptw_solution)
            if round(mdvrptw_solution.get_travel_distance(),8) < round(cost,8):
                got_improvement= True
                break
            
            drop_one_point_intra_depot_mdvrptw(mdvrptw_solution)
            if round(mdvrptw_solution.get_travel_distance(),8) < round(cost,8):
                got_improvement= True
                break

            break



        ''' TODO: REMOVE
        Temporary functions for test
        '''

        if round(mdvrptw_solution.get_travel_distance(), 2) != round(mdvrptw_solution.recalculate_travel_distance(), 2):
            print("bad")
            exit(1)

        if not mdvrptw_solution.is_feasible():
            print('bad2')
            exit(1)

        if round(mdvrptw_solution.get_travel_distance(),2) != round(mdvrptw_solution.recalculate_travel_distance(),2):
            print('bad3')
            exit(1)
