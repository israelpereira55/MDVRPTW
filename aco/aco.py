import numpy as np

from vrp import local_search
from aco import Ant

class ACO:
    #ants : List
    #pheromones    [x,y]   

    m : int        # A sum from demands of all routes.]
    ro : double    # evaporation rate < 1
    max_iterations : int # but can also happen the stagnation behavior, where all ants makes the same tour. TODO: implement a way to see that.

    alpha : double # if alpha = 0, the pheromones are not considered
    beta  : double # 
    tau0  : double # initial value for pheromones

    Q : double # constant???
    number_of_vertices : int

    def __init__(self, m, ro, alpha, beta, max_iterations, number_of_vertices, tau0=0.01, Q=1): 
        self.m = m
        self.ro = ro
        self.alpha=alpha
        self.beta = beta
        self.max_iterations = max_iterations
        self.number_of_vertices = number_of_vertices
        self.tau0 = tau0
        self.Q = Q

        self.ants = []
        self.pheromones = np.full((number_of_vertices, number_of_vertices), tau0)
        print(self.pheromones)
        exit(1)


    def inject_initial_population(self, solutions):
        for solution in solutions:
            self.ants.append(Ant(solution))

    def update_pheromones(self):
        for i in range(number_of_vertices):
            for j in range(number_of_vertices):

                self.pheromones[i][j] = (1-self.ro)*self.pheromones[i][j]
                for ant in self.ants:
                     self.pheromones[i][j] += ant.adj_matrix[i][j]*(self.Q / ant.mdvrptw_solution.get_travel_distance())


    def reconstruct_ant(self):


    def run(self):

        for _ in range(max_iterations):
            #construct ants


            #local search
            for ant in self.ants:
                local_search.local_search(ant.mdvrptw_solution)


            #update pheromones
            self.update_pheromones()
    