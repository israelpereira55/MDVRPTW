'''
    A VRPTW Problem solution.
'''

import numpy as np

from vrp import common
import geometry

class VRPTW_Solution:
    #vrptw                     # The VRPTW problem instance.
    #routes                    # list of routes, each route is a list of numbers. Example: [[1,3,2],[4,5]]
    #free_capacities           # list of free capacities each route has.

    number_of_vertices : int   # number of clients +1 (depot)


    def __init__(self, vrptw):
        self.vrptw = vrptw
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


    def insert_client(self, ci, u, route_index):
        vrptw = self.vrptw

        self.routes[route_index].insert(u, ci)
        self.free_capacities[route_index] -= self.vrptw.demands[ci]

        c_i_less1, c_i_plus1 = self.routes[route_index][u-1], self.routes[route_index][u+1]
        self.travel_distance = self.travel_distance \
           + vrptw.distances[c_i_less1][ci] + vrptw.distances[c_i_plus1][ci] \
           - vrptw.distances[c_i_less1][c_i_plus1]


    def remove_client(self, u, route_index):
        vrptw = self.vrptw
        cu = self.routes[route_index][u]

        self.routes[route_index].pop(u)
        self.free_capacities[route_index] += self.vrptw.demands[cu]

        c_u_less1, c_u_plus1 = self.routes[route_index][u-1], self.routes[route_index][u] #after removing cu, u+1 is now u
        self.travel_distance = self.travel_distance \
           - vrptw.distances[c_u_less1][cu] - vrptw.distances[c_u_plus1][cu] \
           + vrptw.distances[c_u_less1][c_u_plus1]


    def get_route_starting_times(self, route_index):
        route = self.routes[route_index]

        route_starting_times = np.zeros((self.number_of_vertices))
        for index in range(1, len(route) -1): #depot removed
            ci = route[index -1]
            cj = route[index]

            bi = route_starting_times[ci]
            route_starting_times[cj] = common.calculate_starting_time(self.vrptw, ci, bi, cj) #bj

        return route_starting_times


    def get_starting_time(self, route_index, u): #returns bu
        route = self.routes[route_index]

        #considering b0 = 0
        bi = 0
        for i in range(1, u+1):
            ci = route[i -1]
            cj = route[i]
            bj = common.calculate_starting_time(self.vrptw, ci, bi, cj)
            bi = bj

        return bj


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
            ci = route[0]
            for j in range(1, len(route)):
                cj = route[j]
                route_distance += self.vrptw.distances[ci][cj]
                ci = cj

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


    def get_client_location(self, ci):
        for route_index, route in enumerate(self.routes):
            for i in range(len(route)):
                if route[i] == ci:
                    return route_index, i

        print("deu ruim location")
        #exit(1)
        return False, False

    def get_client_cluster_id(self, ci_mdvrptw):
        for i in range(1, len(self.vrptw.clustered_clients)):
            ci = self.vrptw.clustered_clients[i]
            if ci == ci_mdvrptw:
                return i

        return False

    def add_client_to_problem(self, city_mdvrptw, city_vrptw, coordinates, time_windows, service, demand, route_index, u):
        vrptw = self.vrptw
        self.number_of_vertices += 1
        vrptw.number_of_clients += 1

        vrptw.coordinates.insert(city_vrptw, coordinates)
        vrptw.time_windows.insert(city_vrptw, time_windows)
        vrptw.services.insert(city_vrptw, service)
        vrptw.demands.insert(city_vrptw, demand)
        vrptw.clustered_clients.insert(city_vrptw, city_mdvrptw)

        vrptw.travel_times = vrptw.distances = geometry.distances.calculate_distance_matrix(vrptw.coordinates)
        self.insert_client(city_vrptw, u, route_index)

    #if we remove the client 5, client 6 will become 5, 7 will become 6...
    def remove_client_from_problem(self, city_vrptw, route_index, u):
        vrptw = self.vrptw
        self.remove_client(u, route_index)

        self.number_of_vertices -= 1
        vrptw.number_of_clients -= 1

        vrptw.coordinates.pop(city_vrptw)
        vrptw.time_windows.pop(city_vrptw)
        vrptw.services.pop(city_vrptw)
        vrptw.demands.pop(city_vrptw)
        vrptw.clustered_clients.pop(city_vrptw)

        for route in self.routes:
            for i in range(1, len(route)-1):
                if route[i] > city_vrptw:
                    route[i] -= 1

        #TODO: make it a list too?
        vrptw.travel_times = vrptw.distances = geometry.distances.calculate_distance_matrix(vrptw.coordinates)


    def is_feasible(self, depot, print_route=False):
        if len(self.routes) > depot.number_of_vehicles:
            return False

        for route in self.routes:
            if not common.is_feasible_by_time_windows(route, self.vrptw):
                if print_route: print("Infeasible route:", route)
                return False

            sum_demands = 0
            for ci in route:
                sum_demands += self.vrptw.demands[ci]
            if sum_demands > depot.vehicle_capacity:
                return False

        return True
