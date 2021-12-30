import numpy as np

import constants
from constants import Settings
from vrp import VRPTW_Solution, common, solomon, MDVRPTW_Solution, local_search

# Initial population by GRASP - IPGRASP
# (m)  number of solutions
def initial_population(mdvrptw, clustered_clients, m, base_alpha=0.5):
    solutions = []
    for i in range(m):
        alpha = base_alpha + (i/(m-1) * (1-base_alpha))
        print("alpha", alpha)

        solutions.append(construct_solution_with_solomon(mdvrptw, clustered_clients, alpha=alpha, max_iterations=1))

    return solutions


def construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings):
    mdvrptw_best_solution = None
    cost = float('inf')

    failed_attempts=0
    for i in range(grasp_settings.max_iterations):
        mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)
        
        while not mdvrptw_solution.is_feasible_by_number_of_vehicles():
            mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)

            failed_attempts += 1
            if failed_attempts > grasp_settings.number_of_attempts:
                print("All attempts got an infeasible solution. Check parameters.")
                exit(1)

        #Check solution
        #====
        mdvrptw_solution.check_clients_solution()
        if not mdvrptw_solution.is_feasible():
            mdvrptw_solution.print_solution()
            print("infeasible???")
            exit(1)
        #==== TODO: REMOVE


        if grasp_settings.local_search == Settings.VND:
            local_search.vnd(mdvrptw_solution)
        else:
            local_search.local_search(mdvrptw_solution)

        new_cost = mdvrptw_solution.get_travel_distance()
        if new_cost < cost:
            mdvrptw_best_solution = mdvrptw_solution
            cost = new_cost

        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("problem")
            print(round(mdvrptw_solution.recalculate_travel_distance(),2), round(mdvrptw_solution.get_travel_distance(),2))
            exit(1)

    return mdvrptw_best_solution


def grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings):
    mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients)
    for vrptw_subproblem in mdvrptw_solution.vrptw_subproblems:
        vrptw_solution = solomon.greedy_randomized_construction_solomon(alpha, vrptw_subproblem, solomon_settings)
        mdvrptw_solution.vrptw_solutions.append(vrptw_solution)

    return mdvrptw_solution
