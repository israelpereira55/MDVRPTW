'''
    A VRPTW Problem solution.
'''

import numpy as np


class VRPTW_Solution:
    #vrptw                     # The VRPTW problem instance.
    #routes                    # list of routes, each route is a list of numbers. Example: [[1,3,2],[4,5]]
    #free_capacities           # list of free capacities each route has.

    global_demand : int        # A sum from demands of all routes.
    number_of_vertices : int   # number of clients +1 (depot)


    def __init__(self, vrptw):
        self.vrptw = vrptw
        self.global_demand = 0

        self.routes = []
        self.free_capacities = []
        self.number_of_vertices = vrptw.number_of_clients +1


    def insert_route(self, route):
        self.routes.append(route)

        demand = 0
        for i in range(len(route)):
            demand += self.vrptw.demands[route[i]]
        self.free_capacities.append(self.vrptw.vehicle_capacity - demand)
        self.global_demand += demand


    def create_tuple_clients_allowed_demand(self, tuple_clients, route_index):
        route = self.routes[route_index] 
        free_capacity = self.free_capacities[route_index] 

        corrected_tuple = []
        for i in range(len(tuple_clients)):
            client = tuple_clients[i][0]

            if self.vrptw.demands[client] <= free_capacity: #Demand restriction
                corrected_tuple.append(tuple_clients[i])

        return corrected_tuple

    #ej : TW earliest earliest time of service of client j
    #bi : initiation time service of client i
    #si : service time of client i
    #tij: travel time from i to j
    def calculate_starting_time(self, i, bi, j, route_index): #bj-*********************
        route = self.routes[route_index]
        ej = self.vrptw.time_windows[j][0]
        #bi = route_starting_times[i]
        si = self.vrptw.services[i]
        tij = self.vrptw.travel_times[i][j]
        return max(ej, bi+si+tij)

    def get_route_starting_times(self, route_index):
        route = self.routes[route_index]
        route_size = len(route)

        route_starting_times = np.zeros((self.number_of_vertices))
        for index in range(1, route_size -1): #depot removed
            i = route[index -1]
            j = route[index]

            bi = route_starting_times[i]
            route_starting_times[j] = self.calculate_starting_time(i, bi, j, route_index) #bj

        return route_starting_times


    # Presentation functions
    def get_route_bland_string(self, route_index):
        route = self.routes[route_index]

        string = str(route[0])
        for client in range(1, len(route)):
            string += " - " + str(route[client])

        return string

    def print_solution(self):
        route_distance = 0
        sum_route_distances = 0
        for i in range(len(self.routes)):
            route = self.routes[i]

            print("ROUTE #{}:".format(i))
            string = str(route[0])
            for j in range(1, len(route)):
                string += " - " + str(route[j])
                route_distance += self.vrptw.distances[j-1][j]

            sum_route_distances += route_distance
            print(string, "  Travelled distance: {}, Demand: {}, Free: {}".format(round(route_distance,2), self.vrptw.vehicle_capacity - self.free_capacities[i], self.free_capacities[i]))
        print("\nTotal travelled distance:", round(sum_route_distances,2))