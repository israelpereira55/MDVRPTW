import numpy as np

import constants
from vrp import VRPTW_Solution, common, solomon, MDVRPTW_Solution, local_search


def construct_solution_with_solomon(mdvrptw, clustered_clients, alpha=0.95, max_iterations=50):
    mdvrptw_best_solution = None
    cost = float('inf')

    for i in range(max_iterations):
        mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients[:], alpha)
        local_search.vnd(mdvrptw_solution)
        #local_search.local_search(mdvrptw_solution)
        new_cost = mdvrptw_solution.get_travel_distance()
        #print("GRASP VALUE", new_cost)

        if new_cost < cost:
            mdvrptw_best_solution = mdvrptw_solution
            cost = new_cost

        if round(mdvrptw_solution.recalculate_travel_distance(),2) != round(mdvrptw_solution.get_travel_distance(),2):
            print("problem")
            print(round(mdvrptw_solution.recalculate_travel_distance(),2), round(mdvrptw_solution.get_travel_distance(),2))
            exit(1)

    return mdvrptw_best_solution


def grasp_mdvrptw(mdvrptw, clustered_clients, alpha):
    mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients)
    for vrptw_subproblem in mdvrptw_solution.vrptw_subproblems:
        vrptw_solution = solomon.greedy_randomized_construction_solomon(alpha, vrptw_subproblem, alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1, 
                        init_criteria=constants.Solomon.FARTHEST_CLIENT)
        mdvrptw_solution.vrptw_solutions.append(vrptw_solution)

    return mdvrptw_solution
