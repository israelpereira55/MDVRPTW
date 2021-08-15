#pip3 install absl-py

from absl import app, flags
FLAGS = flags.FLAGS

flags.DEFINE_string("instance", None, help="Path to the instance file")
flags.DEFINE_string("type", None, 'Especify the type of the problem (VRPTW or MDVRPTW).')
flags.DEFINE_boolean("toy", False, 'Run with a toy example instead of an instance.')
#flags.DEFINE_boolean("debug", True, 'Boolean flag.')
#flags.DEFINE_boolean("debug_level2", False, 'Boolean flag.')


from vrp import MDVRPTW, VRPTW, solomon, plot
from vrp import MDVRPTW_Solution

from vrp import clusterize
from sklearn.cluster import AffinityPropagation, Birch, AgglomerativeClustering, KMeans

def main(argv):

    mdvrptw_instance = None
    if FLAGS.instance is not None:
            mdvrptw_instance = MDVRPTW(FLAGS.instance) #depot
            #vrptw_instance.read_instance(FLAGS.instance)
    else:
        print("Please describe the MDVRPTW instace file.\nAborting...")
        exit(1)

    mdvrptw_instance.print_instance()
    
    # ============ DEFINING CLUSTERINGS ===================
    #ScikitLearn clusters
    initial_clusters = clusterize.get_initial_depots(mdvrptw_instance)

    #model = Birch(threshold=0.01, n_clusters=mdvrptw_instance.number_of_depots) #fit and predict
    #model = AgglomerativeClustering(n_clusters=mdvrptw_instance.number_of_depots) #fit_predict
    model = KMeans(n_clusters=mdvrptw_instance.number_of_depots, init=initial_clusters, n_init=1) #fit and predict

    #clustered_clients = clusterize.clusterize_by_scikitlearn(mdvrptw_instance, model, show_test=True)
    #print(clustered_clients)
    #Custom cluster method out of scikitlearn
    clustered_clients = mdvrptw_instance.create_cluster_by_urgencies()
    # =====================================================

    mdvrptw_solution = MDVRPTW_Solution(mdvrptw_instance, clustered_clients)
    plot.plot_clusterization_with_line(clustered_clients, mdvrptw_instance.coordinates, mdvrptw_instance.depots)
    mdvrptw_solution.construct_solution_with_solomon(alpha1=0.5, alpha2=0.5, mu=1, lambdaa=1, debug=False, debug_level2=False)
    mdvrptw_solution.print_solution()
    plot.plot_mdvrptw_solution(mdvrptw_solution)


if __name__ == "__main__":
    app.run(main)
