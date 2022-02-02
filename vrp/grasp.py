import time
import random, math
import numpy as np

import constants
from constants import Settings
from vrp import VRPTW_Solution, common, solomon, MDVRPTW_Solution, local_search

from vrp import plot
import matplotlib.pyplot as plt


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
def initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings, print_progress=False):
    solutions = []
    m, base_alpha = grasp_settings.m, grasp_settings.base_alpha
    max_iterations = grasp_settings.max_iterations
    grasp_settings.max_iterations=10

    initial_alpha = grasp_settings.alpha
    best_cost = float('inf')
    for i in range(m):
        alpha = base_alpha + (i/(m-1) * (1-base_alpha))

        grasp_settings.alpha = alpha
        solution = construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        solutions.append(solution)

        cost = solution.get_travel_distance()
        if cost < best_cost:
            best_cost = cost
            best_solution = solution

        if print_progress: print("alpha", alpha, solutions[i].get_travel_distance())

    grasp_settings.max_iterations = max_iterations
    grasp_settings.alpha = initial_alpha
    return solutions, best_solution

def reactive_grasp_select_alpha(alphas, probabilities):
    m = len(probabilities)

    values = np.zeros((m), dtype=int)
    for i in range(m):
        values[i] = i

    choice = random.choices(values, probabilities)[0]
    return alphas[choice], choice

    '''
    sorted_list = np.zeros((m,2))
    for i in range(m):
        sorted_list[i] = probabilities[i], i
    sorted_list = sorted(sorted_list, key=lambda x: x[0]) #crescente "não decrescente"

    p = random.uniform(0,1)

    pbase = 0.
    for i in range(len(probabilities)):
        prob, i = sorted_list[i]
        i = int(i)

        if p <= prob + pbase:
            return alphas[i], i

        pbase += prob

    return alphas[-1], len(alphas) -1
    '''


def reactive_grasp_update_probabilities(probabilities, values_sum, number_of_solutions, best_cost, gamma):
    m = len(probabilities)

    qis = np.zeros((m))
    for i in range(len(probabilities)):
        qi = math.pow(best_cost/ (values_sum[i] + number_of_solutions[i]), gamma)
        qis[i] = qi

    q_sum = sum(qis)

    for i in range(len(probabilities)):
        qi = qis[i]
        probabilities[i] = qi/q_sum


def reactive_grasp(mdvrptw, clustered_clients, grasp_settings, solomon_settings):
    time_start = time.time()

    alphas = []
    m, base_alpha = grasp_settings.m, grasp_settings.base_alpha
    gamma = 10

    initial_alpha = grasp_settings.alpha
    for i in range(m):
        alphas.append(base_alpha + (i/(m-1) * (1-base_alpha)))

    probabilities = np.full((m), 1/m)
    best_cost = float('inf')
    values_sum = np.zeros((m)) # the average cost solutions for each alpha

    #Generating a solution for each alpha to select the initial values.
    max_iterations = grasp_settings.max_iterations
    grasp_settings.max_iterations = 1
    solutions, best_solution = initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
    grasp_settings.max_iterations = max_iterations
    best_cost = best_solution.get_travel_distance()

    for i in range(len(probabilities)):
        values_sum[i] = solutions[i].get_travel_distance()

    number_of_solutions = np.full((m), 1) #for each alpha, the number of solutions generated with that alpha
    reactive_grasp_update_probabilities(probabilities, values_sum, number_of_solutions, best_cost, gamma)

    it = 0
    failed_attempts = 0
    while it < grasp_settings.max_iterations:
        for i in range(100):
            alpha, alpha_index = reactive_grasp_select_alpha(alphas, probabilities)

            mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings)
            while not mdvrptw_solution.is_feasible_by_number_of_vehicles():
                mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings)

                failed_attempts += 1
                if failed_attempts > grasp_settings.number_of_attempts:
                    print(f"[GRASP]: Iteration={i}. Number of infeasible generated solutions surpassed the maximum allowed: {grasp_settings.number_of_attempts}. Aborting...")
                    exit(1)

            if grasp_settings.local_search == Settings.VND:
                local_search.vnd(mdvrptw_solution)
            else:
                local_search.local_search(mdvrptw_solution)

            number_of_solutions[alpha_index] += 1
            values_sum[alpha_index] += mdvrptw_solution.get_travel_distance()

            new_cost = mdvrptw_solution.get_travel_distance()
            if new_cost < best_cost:
                best_solution = mdvrptw_solution
                best_cost = new_cost

                time_end = time.time()
                print(f"[REACTIVE GRASP]: Improved solution {round(best_cost,2)} (iteration={it+i}, alpha={round(alpha,3)}, time={round(time_end-time_start,2)})")

            #print("[RGRASP]", mdvrptw_solution.get_travel_distance(), 'iteration', it+i, 'alpha', round(alpha,3))

        #Updating probabilities
        reactive_grasp_update_probabilities(probabilities, values_sum, number_of_solutions, best_cost, gamma)
        it += 100

    print(f'[REACTIVE GRASP]: Number of infeasible generated solutions={failed_attempts}.')
    return best_solution

