
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
def calculate_starting_time(vrptw, ci, bi, cj): #bj-*********************
    ej = vrptw.time_windows[cj][0]
    si = vrptw.services[ci]
    tij = vrptw.travel_times[ci][cj]
    return max(ej, bi+si+tij)


def calculate_starting_time_mdvrptw(mdvrptw, ci, bi, cj): #bj-*********************
    if cj > mdvrptw.number_of_clients:
        depot_index = cj - mdvrptw.number_of_clients -1
        depot = mdvrptw.depots[depot_index]
        ej = depot.ready_time
    else:
        ej = mdvrptw.time_windows[cj][0]

    if ci > mdvrptw.number_of_clients:
        depot_index = ci - mdvrptw.number_of_clients -1
        depot = mdvrptw.depots[depot_index]
        si = depot.service_time
    else:
        si = mdvrptw.services[ci]

    tij = mdvrptw.travel_times[ci][cj]
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


def is_insertion_viable_by_demand(vrptw_solution, ci, route_index):
    if vrptw_solution.free_capacities[route_index] < vrptw_solution.vrptw.demands[ci]:
        return False
    else:
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
def is_insertion_viable_by_time_windows(vrptw_solution, city, u, route_index, get_values=False):
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    route_starting_times = vrptw_solution.get_route_starting_times(route_index)

    ci = route[u-1] #left neighbour of index u
    bi = route_starting_times[ci]
    bu = calculate_starting_time(vrptw, ci, bi, city)
    if bu > vrptw.time_windows[city][1]: #start time higher than last time of service
        if get_values: 
            return False, None
        else: 
            return False

    cj = route[u]
    bju = calculate_starting_time(vrptw, city, bu, cj)
    bj = route_starting_times[cj]
    PF = bju - bj

    for temp_index in range(u, len(route)):
        j_temp = route[temp_index]
        if route_starting_times[j_temp] + PF > vrptw.time_windows[j_temp][1]:
            if get_values: 
                return False, None
            else: 
                return False

    if get_values:
        return True, [ci, bi, cj, bj, city, bu, bju]
    else:
        return True


# Function: is_insertion_viable_by_time_windows_mdvrptw
#
#   * Descrption: 
#       - Check time windows viability to insert city cm, to position (routeu_index, u), increasing the route size.
#       - All cities which perform mdvrptw actions need to have their indexes for the mdvrptw problem
#         Otherwise, if they are performing vrptw actions, they need to have their indexes from that vrptw subproblem.
#
#   * Restrictions:
#       - city should not be on route already.
#       - u can not be 0 or len(routeu) (Because it is the depot index)
#       - city should be the real index from mdvrptw problem
#
def is_insertion_viable_by_time_windows_mdvrptw(mdvrptw_solution, problem_index, city, route_index, u):
    mdvrptw = mdvrptw_solution.mdvrptw
    vrptw_solution = mdvrptw_solution.vrptw_solutions[problem_index]
    vrptw = vrptw_solution.vrptw
    route = vrptw_solution.routes[route_index]
    route_starting_times = vrptw_solution.get_route_starting_times(route_index)


    ci = route[u-1] #left neighbour of index u
    ci_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=problem_index, ci_vrptw=ci)

    bi = route_starting_times[ci]
    bu = calculate_starting_time_mdvrptw(mdvrptw, ci_mdvrptw, bi, city)
    if bu > mdvrptw.time_windows[city][1]: #start time higher than last time of service
        return False

    cj = route[u]
    cj_mdvrptw = mdvrptw_solution.get_client_id_mdvrptw(depot_index=problem_index, ci_vrptw=cj)
    bju = calculate_starting_time_mdvrptw(mdvrptw, city, bu, cj_mdvrptw)
    bj = route_starting_times[cj]
    PF = bju - bj

    for temp_index in range(u, len(route)):
        j_temp = route[temp_index]
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

    ci = routeu[u-1] #left neighbour of index u
    bi = routeu_starting_times[ci]
    bm = calculate_starting_time(vrptw, ci, bi, cm)
    if bm > vrptw.time_windows[cm][1]: #start time higher than last time of service
        return False

    cj = routeu[u+1]
    bjm = calculate_starting_time(vrptw, cm, bm, cj)
    bj = routeu_starting_times[cj]
    PF = bjm - bj

    for temp_index in range(u+1, len(routeu)):
        j_temp = routeu[temp_index]
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

    vrptw_solution.routes[route_index][p], vrptw_solution.routes[route_index][q] = cq, cp #temporary swap to receive the correct route starting times
    route_starting_times = vrptw_solution.get_route_starting_times(route_index) # TODO da pra fazer uma vez só global?
    
    for i in range(len(route)):
        ci = route[i]
        bi = route_starting_times[ci]
        if bi > vrptw.time_windows[ci][1]: #start time higher than last time of service
            vrptw_solution.routes[route_index][p], vrptw_solution.routes[route_index][q] = cp, cq #un-doing temporary swap
            return False

    vrptw_solution.routes[route_index][p], vrptw_solution.routes[route_index][q] = cp, cq #un-doing temporary swap
    return True


def is_feasible_by_time_windows(route, vrptw, i=0, bi=0):
    ci = route[i]
    #bi = 0 #considering depot has si = ei = 0

    for j in range(1, len(route)):
        cj = route[j]
        bj = calculate_starting_time(vrptw, ci, bi, cj)
        if bj > vrptw.time_windows[cj][1]: #start time higher than last time of service
            return False

        ci,bi = cj,bj # change python maybe? :v

    return True


def get_client_id_vrptw(ci, cluster):
    for ci_vrptw, ci_mdvrptw in enumerate(cluster):
        if ci == ci_mdvrptw:
            return ci_vrptw

    return None

def convert_route_to_vrptw(route, cluster):
    for i in range(len(route)):
        route[i]  = get_client_id_vrptw(route[i], cluster)
