import time, random

from absl import app, flags
FLAGS = flags.FLAGS

flags.DEFINE_string("instance", None, help="Path to the instance file")
flags.DEFINE_boolean("toy", False, 'Run with a toy example instead of an instance.')
#flags.DEFINE_enum('cluster', 'kmeans', ['kmeans', 'urgencies', 'other'], 'Cluster method to be utilized.')


from vrp import MDVRPTW, VRPTW, solomon, plot
from vrp import MDVRPTW_Solution

from vrp import clusterize, local_search, grasp
from sklearn.cluster import AffinityPropagation, Birch, AgglomerativeClustering, KMeans

from constants import Settings
from settings import SoftwareSettings, ACOSettings, GRASPSettings, SolomonSettings


def initial_population_grasp_aco(mdvrptw, clustered_clients, m, base_alpha=0.5):
    solutions = initial_population(mdvrptw, clustered_clients, m, base_alpha)




def main(argv):

    mdvrptw = None
    if FLAGS.instance is not None:
            mdvrptw = MDVRPTW(FLAGS.instance) #depot
    else:
        print("Please describe the MDVRPTW instace file.\nAborting...")
        exit(1)

    software = SoftwareSettings('./settings/software.json')
    grasp_settings = GRASPSettings('./settings/grasp.json')
    aco_settings = ACOSettings('./settings/aco.json')
    solomon_settings = SolomonSettings('./settings/solomon.json')
    
    mdvrptw.print_instance()
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

    #plot.plot_clusterization(clustered_clients, mdvrptw.coordinates, mdvrptw.depots)
    #plot.plot_clusterization_with_line(clustered_clients, mdvrptw.coordinates, mdvrptw.depots)
    # =====================================================

    #SOLUTION METHOD
    '''
    if software.solve_method == Settings.GRASP:
        mdvrptw_solution = grasp.construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        mdvrptw_solution.print_solution()
        plot.plot_mdvrptw_solution(mdvrptw_solution)
    else: #ACO
        exit(1)

    exit(1)
    '''



    best_value = float('inf')
    time_start = time.time()
    sum_value = 0
    for i in range(10):
        #print("seed", i)
        random.seed(i)
        mdvrptw_solution = grasp.construct_solution_with_solomon(mdvrptw, clustered_clients, grasp_settings, solomon_settings)
        sum_value += mdvrptw_solution.get_travel_distance()
        print(mdvrptw_solution.get_travel_distance())

        if mdvrptw_solution.get_travel_distance() < best_value:
            best_value = mdvrptw_solution.get_travel_distance()

        if not mdvrptw_solution.is_feasible():
            print("not feasible")
            exit(1)


    print("media")
    print(sum_value/10)
    time_end = time.time()
    print("Constructive time:", (time_end - time_start)/10)
    print("Best value", round(best_value,2))
    exit(1)


if __name__ == "__main__":
    app.run(main)
