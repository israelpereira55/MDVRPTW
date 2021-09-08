
# Function: is_swap_viable_by_demand
#
#   * Description:
#       - Calculate the starting time of service (bj) of client cj.
#
#   * Variables:
#       - ej : TW earliest earliest time of service of client j
#       - bi : initiation time service of client i
#       - si : service time of client i
#       - tij: travel time from i to j
#
def calculate_starting_time(vrptw, i, bi, j): #bj-*********************
    ej = vrptw.time_windows[j][0]
    si = vrptw.services[i]
    tij = vrptw.travel_times[i][j]
    return max(ej, bi+si+tij)



# ================= FEASBILITY CHECK =================

# Function: is_swap_viable_by_demand
#
#   * Description:
#       - Check demand viability to insert cm to position (routeu_index,u). So, cm will be on the route, taking out cu.
#
#   * Restrictions: 
#       - routei_index != routej_index: 
#           If they are on the same route, the swap won't change viability.
#           You should not call the function if they are on the same route. But if you do so while the route
#           is infeasible, it will return False.
#       
def is_swap_viable_by_demand(vrptw_solution, ci, routei_index, cj, routej_index):
    if vrptw_solution.free_capacities[routej_index] + vrptw_solution.vrptw.demands[cj] < vrptw_solution.vrptw.demands[ci] or  \
       vrptw_solution.free_capacities[routei_index] + vrptw_solution.vrptw.demands[ci] < vrptw_solution.vrptw.demands[cj]:
        return False

    return True


# Function: is_insertion_viable_by_time_windows
#
#   * Descrption: 
#       - Check time windows viability to insert city cm, to position (routeu_index, u), increasing the route size.
#
#   * Restrictions:
#       - city should not be on route already.
#       - u can not be 0 or len(routeu) (Because it is the depot index)
#
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

    for temp_index in range(u, len(route)):
        j_temp = int(route[temp_index])
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

    return True


# Function: is_insertion_swap_viable_by_time_windows
#
#   * Descrption: 
#       - Check time windows viability to swap city cm, to position (routeu_index, u), taking cu out of the route.
#
#   * Restrictions:
#       - cm should not be on routeu already.
#       - u can not be 0 or len(routeu) (Because it is the depot index)
#       - m can not be u.
#
def is_insertion_swap_viable_by_time_windows(vrptw_solution, cm, routem_index, u, routeu_index):
    vrptw = vrptw_solution.vrptw
    routeu = vrptw_solution.routes[routeu_index]
    routeu_starting_times = vrptw_solution.get_route_starting_times(routeu_index) # TODO da pra fazer uma vez só global?

    ci = int(routeu[u-1]) #left neighbour of index u
    bi = routeu_starting_times[ci]
    bm = calculate_starting_time(vrptw, ci, bi, cm)
    if bm > vrptw.time_windows[cm][1]: #start time higher than last time of service
        return False

    cj = int(routeu[u+1])
    bjm = calculate_starting_time(vrptw, cm, bm, cj)
    bj = routeu_starting_times[cj]
    PF = bjm - bj

    for temp_index in range(u+1, len(routeu)):
        j_temp = int(routeu[temp_index])
        if routeu_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

    return True


# Function: is_swap_viable_by_time_windows_same_route
#
#   * Descrption: 
#       - Check time windows viability to swap city cp x cq on routes[route_index].
#
#   * Restrictions:
#       - cp or cq should not be the depot.
#       - cp and cq must be on the same route.
#
def is_swap_viable_by_time_windows_same_route(vrptw_solution, cp, p, cq, q, route_index):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    route_starting_times = vrptw_solution.get_route_starting_times(route_index) # TODO da pra fazer uma vez só global?

    if p > q:
        cp, p, cq, q = cq, q, cp, p

    #Putting q on p position. (p < q)
    ci = int(route[p-1])
    bi = route_starting_times[ci]
    bq = calculate_starting_time(vrptw, ci, bi, cq)

    if bq > vrptw.time_windows[cq][1]: #start time higher than last time of service
        return False

    cj = int(route[p+1])
    bjq = calculate_starting_time(vrptw, cq, bq, cj)
    bj = route_starting_times[cj]
    PF = bjq - bj

    for temp_index in range(p+1, q):
        j_temp = int(route[temp_index])
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            return False

    ''' Aqui serve PF? TODO: pensar
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

    ci = int(route[q-1])
    bi = route_starting_times[ci]
    for u in range(q, len(route)):
        cu = int(route[u])
        bu = calculate_starting_time(vrptw, ci, bi, cu)
        if bu > vrptw.time_windows[cu][1]: #start time higher than last time of service
            return False

        ci, bi = cu, bu
