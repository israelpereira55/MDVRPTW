from absl import app, flags
FLAGS = flags.FLAGS

flags.DEFINE_string("instance", None, help="Path to the instance file")
flags.DEFINE_boolean("toy", False, 'Run with a toy example instead of an instance.')
flags.DEFINE_enum('cluster', 'kmeans', ['kmeans', 'urgencies', 'other'], 'Cluster method to be utilized.')


from vrp import MDVRPTW, VRPTW, solomon, plot
from vrp import MDVRPTW_Solution

from vrp import clusterize, local_search
from sklearn.cluster import AffinityPropagation, Birch, AgglomerativeClustering, KMeans



def main(argv):

    mdvrptw = None
    if FLAGS.instance is not None:
            mdvrptw = MDVRPTW(FLAGS.instance) #depot
    else:
        print("Please describe the MDVRPTW instace file.\nAborting...")
        exit(1)

    mdvrptw.print_instance()
    
    # ============ DEFINING CLUSTERS =====================
    # ScikitLearn clusters
    if FLAGS.cluster == 'kmeans':
        initial_clusters = clusterize.get_initial_depots(mdvrptw)
        model = KMeans(n_clusters=mdvrptw.number_of_depots, init=initial_clusters, n_init=1) #fit and predict
        clustered_clients = clusterize.clusterize_by_scikitlearn(mdvrptw, model, show_warns=True)

    elif FLAGS.cluster == 'urgencies':
        # GIOSA, 2002
        # Article: New assignment algorithms for the multi-depot vehicle routing problem
        clustered_clients = clusterize.clusterize_by_urgencies(mdvrptw)

    elif FLAGS.cluster == 'other': #TODO: Needs fixing
        model = Birch(threshold=0.01, n_clusters=mdvrptw.number_of_depots) #fit and predict
        #model = AgglomerativeClustering(n_clusters=mdvrptw.number_of_depots) #fit_predict

        clustered_clients = clusterize.clusterize_by_scikitlearn_ordering_depots(mdvrptw, model, show_warns=True)
        print(clustered_clients)

    #plot.plot_clusterization(clustered_clients, mdvrptw.coordinates, mdvrptw.depots)
    plot.plot_clusterization_with_line(clustered_clients, mdvrptw.coordinates, mdvrptw.depots)
    # =====================================================

    mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients)
    mdvrptw_solution.construct_solution_with_solomon(alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1)
    mdvrptw_solution.print_solution()
    plot.plot_mdvrptw_solution(mdvrptw_solution)

    solution = local_search.two_opt_mdvrptw(mdvrptw_solution)
    mdvrptw_solution.print_solution()
    plot.plot_mdvrptw_solution(mdvrptw_solution)




if __name__ == "__main__":
    app.run(main)
