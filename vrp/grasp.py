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

    sum_solutions = 0
    failed_attempts=0
    constructed_viable_solution = False
    if print_progress: time_start = time.time()

    for i in range(grasp_settings.max_iterations):
        mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)

        while not mdvrptw_solution.is_feasible_by_number_of_vehicles():
            mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, grasp_settings.alpha, solomon_settings)

            failed_attempts += 1
            if failed_attempts > grasp_settings.number_of_attempts:
                if print_progress:
                    print(f"[GRASP]: Iteration={i}. Number of infeasible generated solutions surpassed the maximum allowed: {grasp_settings.number_of_attempts}. Aborting...")
                
                if constructed_viable_solution:
                    return mdvrptw_best_solution
                else:
                    return None

        constructed_viable_solution = True
        if grasp_settings.local_search == Settings.VND:
            local_search.vnd(mdvrptw_solution)
        else:
            local_search.local_search(mdvrptw_solution)

        new_cost = mdvrptw_solution.get_travel_distance()
        sum_solutions += new_cost
        if new_cost < cost:
            mdvrptw_best_solution = mdvrptw_solution
            cost = new_cost
            if print_progress:
                time_end = time.time()
                print(f"[GRASP]: Improved solution {round(cost,2)} (iteration={i}, time={round(time_end-time_start,2)})")

    if print_progress: 
        print(f'\n[GRASP]: Number of infeasible generated solutions={failed_attempts}.\n'
              f'[GRASP]: Average cost of solutions={round(sum_solutions/grasp_settings.max_iterations, 2)}.')

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
    m, base_alpha = grasp_settings.m, grasp_settings.base_alpha
    max_iterations = grasp_settings.max_iterations
    grasp_settings.max_iterations=1

    solutions = [None]*m
    best_solution = None
    best_cost = float('inf')
    initial_alpha = grasp_settings.alpha
    for i in range(m):
        alpha = base_alpha + (i/(m-1) * (1-base_alpha))

        grasp_settings.alpha = alpha
        solution = construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        solutions[i] = solution

        if solution != None:
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

def reactive_grasp(mdvrptw, clustered_clients, grasp_settings, solomon_settings, print_progress=False):
    time_start = time.time()

    alphas = []
    m, base_alpha = grasp_settings.m, grasp_settings.base_alpha
    gamma = 10

    initial_alpha = grasp_settings.alpha
    for i in range(m):
        alphas.append(base_alpha + (i/(m-1) * (1-base_alpha)))

    probabilities = np.full((m), 1/m)
    values_sum = np.zeros((m)) # initializating the average cost solutions for each alpha

    # Fixing the Reactive GRASP absolute qualification rule.
    # by generating one solution for each alpha to select the initial values. If its infeasible, the value solution will be None.
    # and the cost will be used as a high value.
    solutions, best_solution = initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings)

    if best_solution is None:
        print("[REACTIVE GRASP]: Could not generate any feasible solution. Please check parameters.\n")
        return None

    best_cost = best_solution.get_travel_distance()
    time_end = time.time()

    if print_progress: print(f"[REACTIVE GRASP]: Improved solution {round(best_cost,2)} (iteration={0}, time={round(time_end-time_start,2)})")

    for i in range(len(probabilities)):
        if solutions[i] != None:
            values_sum[i] = solutions[i].get_travel_distance()
        else:
            values_sum[i] = best_cost*10

    number_of_solutions = np.full((m), 1) #for each alpha, the number of solutions generated with that alpha. It started with 1 because the initial population.
    reactive_grasp_update_probabilities(probabilities, values_sum, number_of_solutions, best_cost, gamma)

    it = 0
    sum_solutions = 0
    failed_attempts = 0
    total_failed_attemps = 0
    while it < grasp_settings.max_iterations:
        for i in range(grasp_settings.block_solutions):
            alpha, alpha_index = reactive_grasp_select_alpha(alphas, probabilities)

            mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings)
            failed_attempts = 0
            while not mdvrptw_solution.is_feasible_by_number_of_vehicles():

                # If the alpha selected was infeasible, it's probability will be reduced and a new alpha will be selected.
                # However, when updating the probabilities, the probability will roll back to that value, so we will penalize the cost of that alpha.
                probabilities[alpha_index] = probabilities[alpha_index]/2 
                values_sum[alpha_index] += values_sum[alpha_index]/2

                alpha, alpha_index = reactive_grasp_select_alpha(alphas, probabilities)
                mdvrptw_solution = grasp_mdvrptw(mdvrptw, clustered_clients, alpha, solomon_settings)

                failed_attempts += 1
                total_failed_attemps += 1
                if failed_attempts > grasp_settings.number_of_attempts:
                    print(f"[REACTIVE GRASP]: Iteration={i}. Number of infeasible generated solutions surpassed the maximum allowed: {grasp_settings.number_of_attempts}. Aborting...")
                    return best_solution

            if grasp_settings.local_search == Settings.VND:
                local_search.vnd(mdvrptw_solution)
            else:
                local_search.local_search(mdvrptw_solution)

            number_of_solutions[alpha_index] += 1
            values_sum[alpha_index] += mdvrptw_solution.get_travel_distance()

            new_cost = mdvrptw_solution.get_travel_distance()
            sum_solutions += new_cost

            if new_cost < best_cost:
                best_solution = mdvrptw_solution
                best_cost = new_cost

                time_end = time.time()
                if print_progress: print(f"[REACTIVE GRASP]: Improved solution {round(best_cost,2)} (iteration={it+i}, alpha={round(alpha,3)}, time={round(time_end-time_start,2)})")

            #print("[RGRASP]", mdvrptw_solution.get_travel_distance(), 'iteration', it+i, 'alpha', round(alpha,3))

        #Updating probabilities
        reactive_grasp_update_probabilities(probabilities, values_sum, number_of_solutions, best_cost, gamma)
        it += 100

    if print_progress:
        print(f'\n[REACTIVE GRASP]: Number of infeasible generated solutions={total_failed_attemps}.\n'
        f'[REACTIVE GRASP]: Average cost of solutions={round(sum_solutions/it, 2)}.\n'
        f'[REACTIVE GRASP]: Best solution={round(best_solution.get_travel_distance(), 2)}.')


    return best_solution

