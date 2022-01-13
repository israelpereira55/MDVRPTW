import time
import numpy as np

import constants
from constants import Settings
from vrp import VRPTW_Solution, common, solomon, MDVRPTW_Solution, local_search


def construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings, print_progress=False):
    mdvrptw_best_solution = None
    cost = float('inf')

    failed_attempts=0
    if print_progress: time_start = time.time()
    
    for i in range(grasp_settings.max_iterations):
        mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)
        
        while not mdvrptw_solution.is_feasible_by_number_of_vehicles():
            mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)

            failed_attempts += 1
            if failed_attempts > grasp_settings.number_of_attempts:
                print(f"[GRASP]: Iteration={i}. Number of infeasible generated solutions surpassed the maximum allowed: {grasp_settings.number_of_attempts}. Aborting...")
                exit(1)

        if grasp_settings.local_search == Settings.VND:
            local_search.vnd(mdvrptw_solution)
        else:
            local_search.local_search(mdvrptw_solution)

        new_cost = mdvrptw_solution.get_travel_distance()
        if new_cost < cost:
            mdvrptw_best_solution = mdvrptw_solution
            cost = new_cost
            if print_progress:
                time_end = time.time()
                print(f"[GRASP]: Improved solution {round(cost,2)} (iteration={i}, time={round(time_end-time_start,2)})")

    if print_progress: print(f'[GRASP]: Number of infeasible generated solutions={failed_attempts}.')
    return mdvrptw_best_solution


def grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings):
    mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients)
    for vrptw_subproblem in mdvrptw_solution.vrptw_subproblems:
        vrptw_solution = solomon.greedy_randomized_construction_solomon(alpha, vrptw_subproblem, solomon_settings)
        mdvrptw_solution.vrptw_solutions.append(vrptw_solution)

    return mdvrptw_solution


# Initial population by GRASP - IPGRASP
# (m)  number of solutions
def initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings):
    solutions = []
    m, base_alpha = grasp_settings.m, grasp_settings.base_alpha

    initial_alpha = grasp_settings.alpha
    for i in range(m):
        alpha = base_alpha + (i/(m-1) * (1-base_alpha))

        grasp_settings.alpha = alpha
        solutions.append(construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings))
        print("alpha", alpha, solutions[i].get_travel_distance())

    grasp_settings.alpha = initial_alpha
    return solutions
