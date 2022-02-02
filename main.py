import time, random

from absl import app, flags
FLAGS = flags.FLAGS
flags.DEFINE_string("instance", None, help="Path to the instance file")
flags.DEFINE_boolean("toy", False, 'Run with a toy example instead of an instance.')
flags.DEFINE_boolean("MDVRP", False, 'Run with a toy example instead of an instance.')

from sklearn.cluster import AffinityPropagation, Birch, AgglomerativeClustering, KMeans

from constants import Settings
from vrp import MDVRPTW, MDVRPTW_Solution, VRPTW 
from vrp import solomon, plot, clusterize, local_search, grasp
from settings import SoftwareSettings, ACOSettings, GRASPSettings, SolomonSettings
from aco import ACO


def main(argv):

    mdvrptw = None
    if FLAGS.instance is not None:
        if FLAGS.MDVRP:
            mdvrptw = MDVRPTW(FLAGS.instance, MDVRP=True) #depot
        else:
            mdvrptw = MDVRPTW(FLAGS.instance) #depot
    else:
        print("Please describe the MDVRPTW instace file.\nAborting...")
        exit(1)

    software = SoftwareSettings('./settings/software.json')
    grasp_settings = GRASPSettings('./settings/grasp.json')
    aco_settings = ACOSettings('./settings/aco.json')
    solomon_settings = SolomonSettings('./settings/solomon.json')
    
    #mdvrptw.print_instance()
    random.seed(software.seed)
    # ============ DEFINING CLUSTERS =====================
    # ScikitLearn clusters
    if software.cluster == Settings.KMeans:
        initial_clusters = clusterize.get_initial_depots(mdvrptw)
        model = KMeans(n_clusters=mdvrptw.number_of_depots, init=initial_clusters, n_init=1) #fit and predict
        clustered_clients = clusterize.clusterize_by_scikitlearn(mdvrptw, model, show_warns=True)

    elif software.cluster == Settings.Urgencies:
        # GIOSA, 2002
        # Article: New assignment algorithms for the multi-depot vehicle routing problem
        clustered_clients = clusterize.clusterize_by_urgencies(mdvrptw)

    elif software.cluster == 'other': #TODO: Needs fixing
        model = Birch(threshold=0.01, n_clusters=mdvrptw.number_of_depots) #fit and predict
        #model = AgglomerativeClustering(n_clusters=mdvrptw.number_of_depots) #fit_predict

        clustered_clients = clusterize.clusterize_by_scikitlearn_ordering_depots(mdvrptw, model, show_warns=True)
        print(clustered_clients)
    #plot.plot_instance(mdvrptw, plot_ids=False)
    #plot.plot_clusterization(clustered_clients, mdvrptw.coordinates, mdvrptw.depots)
    #plot.plot_clusterization_with_line(mdvrptw, clustered_clients)
    #exit(1)
    # =====================================================
    mdvrptw.print_instance()

    #SOLUTION METHOD
    if software.solve_method == Settings.GRASP:
        best_solution = grasp.construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings, print_progress=True)
        best_solution.print_solution()
        plot.plot_mdvrptw_solution(best_solution)


    elif software.solve_method == Settings.GRASP_REACTIVE:
        best_solution = grasp.reactive_grasp(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        best_solution.print_solution()
        plot.plot_mdvrptw_solution(best_solution)


    elif software.solve_method == Settings.ACO_AS:
        number_of_vertices = mdvrptw.number_of_clients + mdvrptw.number_of_depots
        aco = ACO(number_of_vertices, aco_settings)
        solutions = grasp.initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        aco.inject_initial_population(solutions)
        aco.run_AS(mdvrptw, clustered_clients, print_progress=True)
        best_solution = aco.best_ant.mdvrptw_solution


    elif software.solve_method == Settings.ACO_ACS:
        number_of_vertices = mdvrptw.number_of_clients + mdvrptw.number_of_depots
        aco = ACO(number_of_vertices, aco_settings)
        #solutions = grasp.initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        #aco.inject_initial_population(solutions)
        aco.run_ACS(mdvrptw, clustered_clients, print_progress=True)
        best_solution = aco.best_ant.mdvrptw_solution


    else: #IPGRASP
        time_start = time.time()
        solutions = grasp.initial_population(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        time_end = time.time()

        best_cost = float('inf')
        for i, solution in enumerate(solutions):
            cost = solution.get_travel_distance()
            if cost < best_cost:
                best_i = i
                best_cost = cost
                best_solution = solution

        alpha = grasp_settings.base_alpha + (best_i/(grasp_settings.m-1) * (1-grasp_settings.base_alpha))
        print(f'[IPGRASP]: Best solution {best_cost} alpha {alpha}')
        print("Time avg:", (time_end - time_start)/aco_settings.m)


    #Test Solution: TEMPORARY
    best_solution.check_clients_solution()
    if round(best_solution.get_travel_distance(), 2) != round(best_solution.recalculate_travel_distance(), 2):
        print("bad")
        exit(1)

    if not best_solution.is_feasible():
        print('bad2')
        exit(1)

if __name__ == "__main__":
    app.run(main)
