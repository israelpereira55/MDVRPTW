import numpy as np
from matplotlib import pyplot



#def two_opt_calculate_a_swap(vrptw_solution, i, routei, j, routej):

#Swap ci x cj. 
#(ixj is position, cixcj is the client)
'''
def check_insertion_viability_demand(vrptw_solution, cm, routem_index, u, routeu_index):
    if routei_index != routej_index and \
       (vrptw_solution.free_capacities[routej_index] < vrptw_solution.vrptw.demands[ci] or  \
        vrptw_solution.free_capacities[routei_index] < vrptw_solution.vrptw.demands[cj]):
       return False

    return True
'''

def is_insertion_swap_viable_by_demand(vrptw_solution, ci, routei_index, cj, routej_index):
    if routei_index != routej_index: #if they are on the same route, the swap won't change viability
        if vrptw_solution.free_capacities[routej_index] < vrptw_solution.vrptw.demands[ci] or  \
           vrptw_solution.free_capacities[routei_index] < vrptw_solution.vrptw.demands[cj]:
            return False

    return True

# u is the index of insertion for city (which CAN NOT be 0). (u IS NOT on the route)
# insert city like u-1 - city - u+1 ->
def is_insertion_viable_by_time_windows(vrptw_solution, city, u, route_index):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    route_starting_times = vrptw_solution.get_route_starting_times(route_index)

    ci = int(route[u-1]) #left neighbour of index u
    bi = route_starting_times[ci]
    bu = vrptw_solution.calculate_starting_time(ci, bi, city, route_index)

    if bu > vrptw.time_windows[u][1]: #start time higher than last time of service
        return False

    cj = int(route[u])
    bju = vrptw_solution.calculate_starting_time(city, bu, cj, route_index)
    bj = route_starting_times[cj]
    PF = bju - bj

    temp_index = u
    #while temp_index < len(route) and (array_routes[0][temp_index] == array_routes[0][temp_index -1]): #while untill the end of the route
    for temp_index in range(u, len(route) -1): #not doing for depot
        j_temp = int(route[temp_index])
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

        temp_index +=1

    return True

# Swap city cm on position u. (i can be on the route) and u won't be on the route on the end
# u can not be 0 or len(route) #depot spots
# m cant be u
def is_insertion_swap_viable_by_time_windows(vrptw_solution, cm, routem_index, u, routeu_index):
    vrptw = vrptw_solution.vrptw
    routeu = vrptw_solution.routes[routeu_index]
    routeu_starting_times = vrptw_solution.get_route_starting_times(routeu_index) # TODO da pra fazer uma vez só global?

    if routem_index != routeu_index:
        ci = int(routeu[u-1]) #left neighbour of index u
        bi = routeu_starting_times[ci]
        bm = vrptw_solution.calculate_starting_time(ci, bi, cm, routeu_index)

        if bm > vrptw.time_windows[cm][1]: #start time higher than last time of service
            return False

        cj = int(routeu[u+1])
        bjm = vrptw_solution.calculate_starting_time(cm, bm, cj, routeu_index)
        bj = routeu_starting_times[cj]
        PF = bjm - bj

#        temp_index = u+1
        #while temp_index < len(route) and (array_routes[0][temp_index] == array_routes[0][temp_index -1]): #while untill the end of the route
        for temp_index in range(u+1, len(routeu)): #not doing for depot
            j_temp = int(routeu[temp_index])
            if routeu_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
                return False

#            temp_index +=1
    else:
        #TODO, but not currently usable
        return False

    return True

# Swap cp x cq, when cp and cq are on the same route
def is_swap_viable_by_time_windows_same_route(vrptw_solution, cp, p, cq, q, route_index):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    route_starting_times = vrptw_solution.get_route_starting_times(route_index) # TODO da pra fazer uma vez só global?
    #if p = q+1?

    if p > q:
        cp, p, cq, q = cq, q, cp, p

    #Putting q on p position. (p < q)
    ci = int(route[p-1])
    bi = route_starting_times[ci]
    bq = vrptw_solution.calculate_starting_time(ci, bi, cq, route_index)

    if bq > vrptw.time_windows[cq][1]: #start time higher than last time of service
        return False

    cj = int(route[p+1])
    bjq = vrptw_solution.calculate_starting_time(cq, bq, cj, route_index)
    bj = route_starting_times[cj]
    PF = bjq - bj

    #while temp_index < len(route) and (array_routes[0][temp_index] == array_routes[0][temp_index -1]): #while untill the end of the route
    for temp_index in range(p+1, q): #not doing for depot
        j_temp = int(route[temp_index])
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

    #Putting p on q position. (p < q)
    #Now i/j is the neighbour of q.
    ci = int(route[q-1])
    bi = route_starting_times[ci]
    bp = vrptw_solution.calculate_starting_time(ci, bi, cp, route_index)

    if bp > vrptw.time_windows[cp][1]: #start time higher than last time of service
        return False

    cj = int(route[q+1])
    bjp = vrptw_solution.calculate_starting_time(cp, bp, cj, route_index)
    bj = route_starting_times[cj]
    PF = bjp - bj

    #Aqui serve PF? TODO: pensar
    for temp_index in range(q+1, len(route)): #not doing for depot
        j_temp = int(route[temp_index])
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

'''
def two_opt_check_viability_time_windows(vrptw_solution, array_solution, i, routei_index, j, routej_index):

    #Checking time windows:
    if routei_index != routej_index:
        routei_starting_times = vrptw_solution.get_route_starting_times(routei_index)
        routej_starting_times = vrptw_solution.get_route_starting_times(routej_index)


        i_less1 = array_solution[i-1] #left neighbour of i
        b_i_less1 = routei_starting_times[i-1]
        b_i_less1_j = solution.calculate_starting_time(i_less1, bi_less1, j, routei_index)

        if b_i_less1_j > vrptw_instance.time_windows[j][1]: #start time higher than last time of service
            return False

        #Calculating Push Foward. Look for Lemma 1.1 on Solomon article.
        bju = solution.calculate_starting_time(u, bu, j, route_index)
        #bj = solution.calculate_starting_time(vrptw_instance, i, bi, j, route_index)
        bj = route_starting_times[j]




    return True
'''

class GotImprovementException(Exception):
    """Base class for other exceptions"""
    pass

def two_opt_vrptw(vrptw_solution):
    vrptw = vrptw_solution.vrptw
    array_solution = vrptw_solution.get_two_array_solution()
    array_routes = vrptw_solution.get_two_array_routes()
    array_routes_without_depot = vrptw_solution.get_two_array_routes_without_depot()


    number_of_clients = vrptw_solution.number_of_vertices -1
    #print("routes")
    #print(vrptw_solution.routes)
    '''
    print('')
    print('array_routes')
    print(array_routes)

    print('array_routes_without_depot')
    print(array_routes_without_depot)

    print("")
    print("array solution")
    print(array_solution)
    '''
    vrptw_solution.print_solution()

    number_of_clients = len(array_routes_without_depot[0])
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
                                if not is_swap_viable_by_time_windows_same_route(vrptw_solution, ci, i, cj, j, routei_index):
                                    continue
                            else:
                                if not is_insertion_swap_viable_by_time_windows(vrptw_solution, ci, routei_index, j, routej_index) or \
                                   not is_insertion_swap_viable_by_time_windows(vrptw_solution, cj, routej_index, i, routei_index):
                                    continue
                                #TODO remover check de rota da funcao de cima

                            #Checking Demand
                            if not is_insertion_swap_viable_by_demand(vrptw_solution, ci, routei_index, cj, routej_index):
                                continue

                            #Calc new cost
                            new_cost = cost \
                                       - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                                       + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                                       - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                                       + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]

                            
                            #print(cost, new_cost)
                            #exit(1)


                            if new_cost < cost:
                                #print("Melhorei eeeee", cost, new_cost)
                                #print("SWAP", ci, cj)

                                vrptw_solution.routes[routei_index][i] = cj
                                vrptw_solution.routes[routej_index][j] = ci # TODO: swap em funcao pra mudar mais coisa
                                cost = new_cost

                                vrptw_solution.travel_distance = cost

                                #got_improvement = True #TODO : reactivate

                                vrptw_solution.print_solution()

                                raise GotImprovementException
                            #exit(1)

                    #print('-')
        except GotImprovementException:
            got_improvement = True

        #print("terminei um ciclo")
        #vrptw_solution.travel_distance = cost
        #TODO, pegar custo da rota ao inves do individuo? acho q n precisa né



        '''
        cost = vrptw_solution.travel_distance
        for i in range(number_of_clients -1): #-1 for depot; (-1) because if i=number of clients, then for j will do nothing.
            ci = int(array_routes_without_depot[1][i])
            routei_index = int(array_routes_without_depot[0][i])
            #route = vrptw_solution.routes[]
            
            for j in range(i+1, number_of_clients):
                cj = int(array_routes_without_depot[1][j])
                routej_index = int(array_routes_without_depot[0][j])

                if not is_insertion_swap_viable_by_time_windows(vrptw_solution, ci, routei_index, j, routej_index) or \
                   not is_insertion_swap_viable_by_time_windows(vrptw_solution, cj, routej_index, i, routei_index):
                    continue

                if not is_insertion_swap_viable_by_demand(vrptw_solution, ci, routei_index, cj, routej_index):
                    continue

                #Calc new cost

                dij = vrptw.distances[i][j]
                cj = int(array_routes_without_depot[1][j])

                new_cost = cost - dij


                print(ci, cj, i, j)

            print('-')
        '''

    #if vrptw_solution.vrptw.index == 0:
    #    vrptw_solution.print_solution()
    #    exit(1)
    #print("terminei um vrptw")
    return vrptw_solution

def two_opt_mdvrptw(mdvrptw_solution):

    for vrptw_solution in mdvrptw_solution.vrptw_solutions:
         two_opt_vrptw(vrptw_solution)

    return mdvrptw_solution

