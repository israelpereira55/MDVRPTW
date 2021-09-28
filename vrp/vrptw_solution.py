'''
    A VRPTW Problem solution.
'''

import numpy as np

from vrp import common


class VRPTW_Solution:
    #vrptw                     # The VRPTW problem instance.
    #routes                    # list of routes, each route is a list of numbers. Example: [[1,3,2],[4,5]]
    #free_capacities           # list of free capacities each route has.

    global_demand : int        # A sum from demands of all routes.
    number_of_vertices : int   # number of clients +1 (depot)


    def __init__(self, vrptw):
        self.vrptw = vrptw
        self.global_demand = 0
        self.travel_distance = 0. #cost

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

    def get_route_starting_times(self, route_index):
        route = self.routes[route_index]
        route_size = len(route)

        route_starting_times = np.zeros((self.number_of_vertices))
        #route_starting_times[0] = self.vrptw.
        for index in range(1, route_size -1): #depot removed
            i = route[index -1]
            j = route[index]

            bi = route_starting_times[i]
            route_starting_times[j] = common.calculate_starting_time(self.vrptw, i, bi, j) #bj

        return route_starting_times

    # Swap city ci=(i, routei_index) x cj=(j, routej_index)
    def swap_two_cities(self, i, routei_index, j, routej_index):
        vrptw = self.vrptw
        ci = self.routes[routei_index][i]
        cj = self.routes[routej_index][j]

        self.routes[routei_index][i] = cj
        self.routes[routej_index][j] = ci

        if routei_index != routej_index:
            self.free_capacities[routei_index] += vrptw.demands[ci] - vrptw.demands[cj]
            self.free_capacities[routej_index] += vrptw.demands[cj] - vrptw.demands[ci]


        c_i_less1 = self.routes[routei_index][i-1]
        c_i_plus1 = self.routes[routei_index][i+1]
        c_j_less1 = self.routes[routej_index][j-1]
        c_j_plus1 = self.routes[routej_index][j+1]

        if (routei_index == routej_index) and (i == j-1):
            self.travel_distance += \
                   - vrptw.distances[c_i_less1][ci] - vrptw.distances[ci][cj] \
                   - vrptw.distances[cj][c_j_plus1] \
                   + vrptw.distances[c_i_less1][cj] + vrptw.distances[cj][ci] \
                   + vrptw.distances[ci][c_j_plus1]

            # TODO, remove vrptw.distances[ci][cj] from above
        else:
            self.travel_distance += \
                   - vrptw.distances[c_i_less1][ci] - vrptw.distances[c_i_plus1][ci] \
                   + vrptw.distances[c_i_less1][cj] + vrptw.distances[c_i_plus1][cj] \
                   - vrptw.distances[c_j_less1][cj] - vrptw.distances[c_j_plus1][cj] \
                   + vrptw.distances[c_j_less1][ci] + vrptw.distances[c_j_plus1][ci]


    # Presentation functions
    def get_route_bland_string(self, route_index):
        route = self.routes[route_index]

        string = str(route[0])
        for client in range(1, len(route)):
            string += " - " + str(route[client])

        return string

    def print_solution(self):
        sum_route_distances = 0
        for i in range(len(self.routes)):
            route_distance = 0
            route = self.routes[i]

            print("ROUTE #{}:".format(i))
            string = str(route[0])
            for j in range(1, len(route)):
                string += " - " + str(route[j])
                ci = route[j-1]
                cj = route[j]
                route_distance += self.vrptw.distances[ci][cj]

            sum_route_distances += route_distance
            print(string, "  Travelled distance: {}, Demand: {}, Free: {}".format(round(route_distance,2), self.vrptw.vehicle_capacity - self.free_capacities[i], self.free_capacities[i]))
        print("\nTotal travelled distance:", round(sum_route_distances,2))


    def calculate_cost(self):
        sum_route_distances = 0
        for route in self.routes:
            route_distance = 0
            for j in range(1, len(route)):
                ci = route[j-1]
                cj = route[j]
                route_distance += self.vrptw.distances[ci][cj]

            sum_route_distances += route_distance

        return sum_route_distances

    def get_two_array_solution(self):
        array_solution = np.zeros((2, self.number_of_vertices)) #2xN, the position 0 is the depot.
        print(self.routes)

        for i in range(len(self.routes)):
            route = self.routes[i]
            index = 1
            for j in range(1, len(route)-1):
                client = route[j]

                array_solution[0][client] = i
                array_solution[1][client] = index
                index +=1

        return array_solution


    def get_two_array_routes_without_depot(self):
        array_routes = np.zeros((2, self.number_of_vertices-1)) #2xN, the position 0 is the depot.
        print(self.routes)

        index = 0
        for i in range(len(self.routes)):
            route = self.routes[i]
            for j in range(1, len(route)-1):
                array_routes[0][index] = i
                array_routes[1][index] = route[j]
                index +=1

        return array_routes

    def get_two_array_routes(self):
        array_size = (self.number_of_vertices -1) + len(self.routes)*2 #number of clients + 2*number os routes (cuz of duplicated depot)
        array_routes = np.zeros((2, array_size)) #All routes in a single array (includes depot on first and last position)

        index = 0
        for i in range(len(self.routes)):
            route = self.routes[i]
            print(route)
            print(len(route))
            for j in range(len(route)):
                array_routes[0][index] = i
                array_routes[1][index] = route[j]
                index +=1

        return array_routes
