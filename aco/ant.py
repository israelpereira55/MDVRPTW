import numpy as np

from vrp import MDVRPTW_Solution

class Ant:
    #mdvrptw_solution # the tuor made by the ant
    #adj_matrix   

    def __init__(self, mdvrptw, clustered_clients): 
        self.mdvrptw_solution = MDVRPTW_Solution(mdvrptw, clustered_clients) #the tuor is empty

        number_of_vertices = mdvrptw.number_of_clients + mdvrptw.number_of_depots
        self.adj_matrix = np.zeros((number_of_vertices,number_of_vertices), dtype=int)


    def __init__(self, mdvrptw_solution):
        self.mdvrptw_solution = mdvrptw_solution
        mdvrptw = mdvrptw_solution.mdvrptw
        number_of_vertices = mdvrptw.number_of_clients + mdvrptw.number_of_depots
        self.adj_matrix = np.zeros((number_of_vertices +1,number_of_vertices +1))

        for index in range(mdvrptw.number_of_depots):
            cluster = self.mdvrptw_solution.clustered_clients[index]
            vrptw_solution = self.mdvrptw_solution.vrptw_solutions[index]
            #vrptw_subproblem = self.vrptw_subproblems[index]

            for route_index, route in enumerate(vrptw_solution.routes):
                ci_mdvrptw = cluster[route[0]]
                for j in range(1,len(route)):
                    cj_mdvrptw = cluster[route[j]]

                    self.adj_matrix[ci_mdvrptw][cj_mdvrptw] = 1 #its not symmetric
                    ci_mdvrptw = cj_mdvrptw