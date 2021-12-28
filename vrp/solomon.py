import numpy as np

import math, random
import constants
from vrp import VRPTW_Solution, common

from operator import itemgetter #to get max in a tuple, stackoverflow says its faster than lambda and pure python, see bellow and check someday 
# https://stackoverflow.com/questions/13145368/find-the-maximum-value-in-a-list-of-tuples-in-python


def get_tuple_of_clients(vrptw):
    tuple_clients = [[0,0]] * (vrptw.number_of_clients)
    for ci in range(1, vrptw.number_of_clients+1):
        tuple_clients[ci -1] = ci, vrptw.distances[0][ci]

    return tuple_clients


def create_route_closest_tw(vrptw, tuple_clients):
    closest_index = -1
    closest_tw = float('inf')

    for i in range(len(tuple_clients)):
        ci = tuple_clients[i][0]
        if vrptw.time_windows[ci][1] < closest_tw:
            closest_index = i
            closest_tw = vrptw.time_windows[ci][1]

    ci = tuple_clients[closest_index][0]
    route = [0] * 3
    route[1] = ci
    tuple_clients.pop(closest_index)
    return route


def create_route_farthest_client(vrptw, ordered_tuple):
    client = ordered_tuple.pop(0)
    route = [0] * 3
    route[1] = client[0]
    return route

def create_tuple_clients_allowed_demand(vrptw_solution, tuple_clients, route_index):
    route = vrptw_solution.routes[route_index] 
    free_capacity = vrptw_solution.free_capacities[route_index] 

    corrected_tuple = []
    for i in range(len(tuple_clients)):
        client = tuple_clients[i][0]

        if vrptw_solution.vrptw.demands[client] <= free_capacity: #Demand restriction
            corrected_tuple.append(tuple_clients[i])

    return corrected_tuple

def create_tuple_ordered_clients_by_distance(vrptw):
    tuple_clients = [[0,0]] * (vrptw.number_of_clients)
    for i in range(1, vrptw.number_of_clients+1):
        tuple_clients[i -1] = i, vrptw.distances[0][i]
    
    ordered_tuple = sorted(tuple_clients, key=lambda tup: tup[1], reverse = True)
    return tuple_clients, ordered_tuple


def calculate_c11(vrptw, i, u, j, mu):
    return vrptw.distances[i][u] + vrptw.distances[u][j] - mu * vrptw.distances[i][j]

'''
def insertion_heuristic_debug(vrptw, alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1, debug=False, debug_level2=False):
    if debug: 
        print("=========== SOLOMON INSERTION HEURISTIC ==============\n\n",
              "Entry Parameters: alpha1 = {}, alpha2 = {}\n".format(alpha1, alpha2),
              "                  mu = {}, lambda = {}\n\n".format(mu, lambdaa))

    vrptw_solution = VRPTW_Solution(vrptw)

    route_index = 0
    #tuple_clients, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
    _, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
    
    #Do while, I miss you </3
    route = create_route_farthest_clienter(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
    vrptw_solution.insert_route(route)
    if debug: 
        route_string = vrptw_solution.get_route_bland_string(route_index)
        print("[SEED]: New Route ", route_string, "\n")

    while len(ordered_tuple) > 0:
        route = vrptw_solution.routes[route_index] #not necessary, actually
        route_starting_times = vrptw_solution.get_route_starting_times(route_index)
        if debug_level2: print("STARTING TIMES: ", route_starting_times)

        c1_list = []
        #Ordered tuple of clients corrected by demand
        corrected_tuple = create_tuple_clients_allowed_demand(vrptw_solution, ordered_tuple, route_index)
        for u_index in range(len(corrected_tuple)):
            u = corrected_tuple[u_index][0]

            if debug_level2: print("  * Checking Client {} on route {}.".format(u, route_index))

            lowest_c1 = (10000, -1, -1) #(c1, route_index, u)
            #testing arc (i,u,j)
            for current_route_index in range(1, len(route)):
                i = route[current_route_index -1]
                j = route[current_route_index]
                if debug_level2: print("     - insertion (i,u,j) = ({},{},{})".format(i,u,j))

                bi = route_starting_times[i]
                bu = vrptw_solution.calculate_starting_time(i, bi, u, route_index)

                if debug_level2: print("       bu lu", bu, vrptw.time_windows[u][1])
                if bu > vrptw.time_windows[u][1]:
                    if debug_level2: print("       infeasible: bu > lu.\n")
                    continue

                #Calculating Push Foward. Look for Lemma 1.1 on Solomon article.
                bju = vrptw_solution.calculate_starting_time(u, bu, j, route_index)
                #bj = vrptw_solution.calculate_starting_time(vrptw, i, bi, j, route_index)
                bj = route_starting_times[j]

                PF = bju - bj

                if debug_level2: print("       bju, bj, PF", bju, bj, PF)

                viable = True
                for temp_index in range(current_route_index, len(route)): #not doing for depot
                    j_temp = route[temp_index]

                    if debug_level2: print("         PF: (bj, bj + PF, lj)", route_starting_times[j_temp], route_starting_times[j_temp] + PF, vrptw.time_windows[j_temp][1])
                    if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
                        viable=False
                        if debug_level2: print("         infeasible: bju > lju.\n")
                        break

                if not viable: #goto feelings.
                    continue

                #If it goes here, then the insertion is viable
                c11 = calculate_c11(vrptw, i, u, j, mu)
                c12 = bju - bj #PF, really?

                c1 = alpha1*c11 + alpha2*c12

                if c1 < lowest_c1[0]:
                    lowest_c1 = (c1, current_route_index, u)

            #Here we have already calculated all c1 for u client
            if lowest_c1[1] != -1: #then we have a viable insertion, which has the minimum c1 for the current u client.
                c1_list.append(lowest_c1)

        #Here we have a lisbvv= max{5,2} = 5, viavel [5,8]t of minimum c1 for all viable clients
        if len(c1_list) > 0:
            c2_list = []
            for c1_triple in c1_list:
                u = c1_triple[2]
                c1 = c1_triple[0]

                c2 = lambdaa * vrptw.distances[0][u] - c1
                triple = (c2, c1_triple[1], u)
                c2_list.append(triple)

            #highest_triple = max(c2_list,key=itemgetter(0))
            highest_triple = max(c2_list)

            if debug_level2:
                print("  Route:", vrptw_solution.routes[route_index])
                print("  C1 List:", c1_list)
                print("  C2 List:", c2_list)
                print("  Selected triple:", highest_triple, "\n")

            optimum_u = highest_triple[2]
            optimum_index = highest_triple[1]

            vrptw_solution.routes[route_index].insert(optimum_index, optimum_u)
            vrptw_solution.free_capacities[route_index] -= vrptw.demands[optimum_u]

            #linkar indices ordered x corrected tuple pra nao percorrer
            for temp in range(len(ordered_tuple)):
                if ordered_tuple[temp][0] == optimum_u:
                    ordered_tuple.pop(temp)
                    break

            if debug: print("[INSERTION]: {}  (client: {})\n".format(vrptw_solution.routes[route_index], optimum_u))
        else:

            if debug: print("[INFEASIBLE CLIENT]: Could not find any viable insertion for the current route.\n                     Starting a new route...\n\n")
            route_index += 1

            route = create_route_farthest_clienter(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
            vrptw_solution.insert_route(route)
            if debug: 
                route_string = vrptw_solution.get_route_bland_string(route_index)
                print("[SEED]: New Route ", route_string, "\n")

    vrptw_solution.travel_distance = vrptw_solution.calculate_cost() #TODO deve dar pra fazer em cima, verificar
    return vrptw_solution 
'''

def insertion_heuristic(vrptw, alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1, 
                        init_criteria=constants.Solomon.FARTHEST_CLIENT):
    vrptw_solution = VRPTW_Solution(vrptw)

    route_index = 0
    #tuple_clients, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
    
    #Do while, I miss you </3
    if init_criteria == constants.Solomon.FARTHEST_CLIENT:
        _, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
        route = create_route_farthest_client(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
        vrptw_solution.insert_route(route)

    elif init_criteria == constants.Solomon.CLOSEST_TW:
        tuple_clients = get_tuple_of_clients(vrptw)
        route = create_route_closest_tw(vrptw, tuple_clients)
        vrptw_solution.insert_route(route)
        ordered_tuple = tuple_clients #TODO: rename to tuple_clients on the whole function


    while len(ordered_tuple) > 0:
        route = vrptw_solution.routes[route_index] #not necessary, actually
        route_starting_times = vrptw_solution.get_route_starting_times(route_index)

        c1_list = []
        #Ordered tuple of clients corrected by demand
        corrected_tuple = create_tuple_clients_allowed_demand(vrptw_solution, ordered_tuple, route_index)
        for u in range(len(corrected_tuple)):
            cu = corrected_tuple[u][0]

            lowest_c1 = (10000, -1, -1) #(c1, route_index, u)
            #testing arc (i,u,j)
            for j in range(1, len(route)):
                is_viable, values = common.is_insertion_viable_by_time_windows(vrptw_solution, cu, j, route_index, get_values=True)
                if is_viable: 
                    ci, bi, cj, bj, cu, bu, bju = values
                else:
                    continue

                #If it goes here, then the insertion is viable
                c11 = calculate_c11(vrptw, ci, cu, cj, mu)
                c12 = bju - bj #just PF, really?
                c1 = alpha1*c11 + alpha2*c12

                if c1 < lowest_c1[0]:
                    lowest_c1 = (c1, j, cu)


            #Here we have already calculated all c1 for u client
            if lowest_c1[1] != -1: #then we have a viable insertion, which has the minimum c1 for the current u client.
                c1_list.append(lowest_c1)

        #Here we have a list of minimum c1 for all viable clients
        if len(c1_list) > 0:
            c2_list = []
            for c1_triple in c1_list:
                cu = c1_triple[2]
                c1 = c1_triple[0]

                c2 = lambdaa * vrptw.distances[0][cu] - c1
                triple = (c2, c1_triple[1], cu)
                c2_list.append(triple)

            #highest_triple = max(c2_list,key=itemgetter(0))
            highest_triple = max(c2_list)
            optimum_u = highest_triple[2]
            optimum_index = highest_triple[1]

            vrptw_solution.routes[route_index].insert(optimum_index, optimum_u)
            vrptw_solution.free_capacities[route_index] -= vrptw.demands[optimum_u]

            #todo: linkar indices ordered x corrected tuple pra nao percorrer
            for temp in range(len(ordered_tuple)):
                if ordered_tuple[temp][0] == optimum_u:
                    ordered_tuple.pop(temp)
                    break
        else:
            route_index += 1

            if init_criteria == constants.Solomon.FARTHEST_CLIENT:
                route = create_route_farthest_client(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
                vrptw_solution.insert_route(route)

            elif init_criteria == constants.Solomon.CLOSEST_TW:
                route = create_route_closest_tw(vrptw, ordered_tuple)
                vrptw_solution.insert_route(route)

    vrptw_solution.travel_distance = vrptw_solution.calculate_cost() #TODO deve dar pra fazer em cima, verificar
    return vrptw_solution 


def greedy_randomized_construction_solomon(alpha, vrptw, alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1, 
                        init_criteria=constants.Solomon.FARTHEST_CLIENT):

    vrptw_solution = VRPTW_Solution(vrptw)

    route_index = 0
    #tuple_clients, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
    
    #Do while, I miss you </3
    if init_criteria == constants.Solomon.FARTHEST_CLIENT:
        _, ordered_tuple = create_tuple_ordered_clients_by_distance(vrptw)
        route = create_route_farthest_client(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
        vrptw_solution.insert_route(route)


    while len(ordered_tuple) > 0:
        route = vrptw_solution.routes[route_index] #not necessary, actually
        route_starting_times = vrptw_solution.get_route_starting_times(route_index)

        c1_list = []
        #Ordered tuple of clients corrected by demand
        corrected_tuple = create_tuple_clients_allowed_demand(vrptw_solution, ordered_tuple, route_index)
        for u in range(len(corrected_tuple)):
            cu = corrected_tuple[u][0]

            lowest_c1 = (10000, -1, -1) #(c1, route_index, u)
            #testing arc (i,u,j)
            for j in range(1, len(route)):
                is_viable, values = common.is_insertion_viable_by_time_windows(vrptw_solution, cu, j, route_index, get_values=True)
                if is_viable: 
                    ci, bi, cj, bj, cu, bu, bju = values
                else:
                    continue

                #If it goes here, then the insertion is viable
                c11 = calculate_c11(vrptw, ci, cu, cj, mu)
                c12 = bju - bj #just PF, really?
                c1 = alpha1*c11 + alpha2*c12

                if c1 < lowest_c1[0]:
                    lowest_c1 = (c1, j, cu)


            #Here we have already calculated all c1 for u client
            if lowest_c1[1] != -1: #then we have a viable insertion, which has the minimum c1 for the current u client.
                c1_list.append(lowest_c1)

        #Here we have a list of minimum c1 for all viable clients
        if len(c1_list) > 0:
            c2_list = []
            for c1_triple in c1_list:
                cu = c1_triple[2]
                c1 = c1_triple[0]

                c2 = lambdaa * vrptw.distances[0][cu] - c1
                triple = (c2, c1_triple[1], cu)
                c2_list.append(triple)

            #highest_triple = max(c2_list,key=itemgetter(0))
            #highest_triple = max(c2_list)

            c2_list.sort(key = lambda x: x[0])
            grasp_num_elementos = math.ceil(len(c2_list)*(1-alpha))
            grasp_index = random.randint(len(c2_list) -grasp_num_elementos, len(c2_list) -1)
            highest_triple = c2_list[grasp_index]

            optimum_u = highest_triple[2]
            optimum_index = highest_triple[1]

            vrptw_solution.routes[route_index].insert(optimum_index, optimum_u)
            vrptw_solution.free_capacities[route_index] -= vrptw.demands[optimum_u]

            #todo: linkar indices ordered x corrected tuple pra nao percorrer
            for temp in range(len(ordered_tuple)):
                if ordered_tuple[temp][0] == optimum_u:
                    ordered_tuple.pop(temp)
                    break
        else:
            route_index += 1

            if init_criteria == constants.Solomon.FARTHEST_CLIENT:
                route = create_route_farthest_client(vrptw, ordered_tuple) #it will remove the first element from ordered tuple
                vrptw_solution.insert_route(route)

            elif init_criteria == constants.Solomon.CLOSEST_TW:
                route = create_route_closest_tw(vrptw, ordered_tuple)
                vrptw_solution.insert_route(route)

    vrptw_solution.travel_distance = vrptw_solution.calculate_cost() #TODO deve dar pra fazer em cima, verificar
    return vrptw_solution 
