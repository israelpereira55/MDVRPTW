import numpy as np
import math

import geometry
from vrp import VRPTW, Depot, MDVRPTW_Solution
from vrp import solomon

'''
    MDVRPTW Class

    It has the information of cordinates and distances for all clients from the global problem. Also, there are 
    the "vrptw_list" in which every depot has a vrptw problem, where the clients are clustered.

    Clients id is in [1,n].
    On MDVRPTW Class, the index 0 has nothing, so all values are zero.
    But on VRPTW Class, the index 0 has the depot.

'''

class MDVRPTW:
    #coordinates   [x,y]   
    #distances      dij     distance matrix
    #time_windows  [ei, li] earliest time of service, latest time of service 
    #services      [si]     service time 
    #demands       [?] 
    #depots

    number_of_vehicles : int
    number_of_clients : int
    number_of_depots : int


    def __init__(self, instance_file):
        self.read_instance(instance_file)


    def read_instance(self, instance_file):
        try:
            file = open(instance_file)
            lines =  file.readlines()
            file.close()
        except IOError:
            print("[ERROR]: Could not open the {} file.".format(instance_file))
            exit(1)


        self.problem_type, self.number_of_vehicles, self.number_of_clients, self.number_of_depots = (int(x) for x in lines[0].split())
        if self.problem_type != 6:
            print("[ERROR] The instance file isn't for MDVRPTW.\nAborting...")
            exit(1)

        vertices_number = self.number_of_clients + self.number_of_depots

        self.coordinates = np.zeros((vertices_number +1 ,2))
        self.time_windows = np.zeros((self.number_of_clients +1,2))
        self.services = np.zeros((self.number_of_clients +1))
        self.demands = np.zeros((self.number_of_clients +1))
        self.depots = [None] * self.number_of_depots


        # Depots
        for i in range(self.number_of_depots):
            route_max_time, vehicle_max_load = (float(x) for x in lines[1+i].split())
            depot = Depot(index=i, route_max_time=route_max_time, vehicle_capacity=vehicle_max_load, number_of_vehicles=self.number_of_vehicles)
            self.depots[i] = depot

        # Clients
        for i in range(self.number_of_clients):
            line = lines[1 + self.number_of_depots + i]
            splited_line = line.split()

            #client_id, x, y, service, demand, frequency_of_visit, list_possible_visits, ready_time, due_date  = [int(x) for x in line.split()]
            client_id, x, y, service, demand, frequency_of_visit, number_of_possible_visits = int(splited_line[0]), float(splited_line[1]), float(splited_line[2]), float(splited_line[3]), float(splited_line[4]), float(splited_line[5]), int(splited_line[6])
            if frequency_of_visit != 1:
                print("[ERROR] Frequency of visit is not 1. Please check.\nAborting...")
                exit(1)
            #for j in range(number_of_possible_visits):
                #ignore
            
            ready_time, due_date = float(splited_line[7 + number_of_possible_visits]), float(splited_line[8 + number_of_possible_visits])

            self.coordinates[client_id] = x,y
            self.time_windows[client_id] = ready_time, due_date
            self.services[client_id] = service
            self.demands[client_id] = demand


        depot_index = 0
        start = 1+ self.number_of_depots +self.number_of_clients
        for i in range(start, start+self.number_of_depots):
            line = lines[i]
            splited_line = line.split()
            depot_customer_id, x, y, service, demand, frequency_of_visit, number_of_possible_visits, ready_time, due_date = int(splited_line[0]), float(splited_line[1]), float(splited_line[2]), float(splited_line[3]), float(splited_line[4]), float(splited_line[5]), int(splited_line[6]),float(splited_line[7]), float(splited_line[8])

            if frequency_of_visit != 0 or number_of_possible_visits != 0:
                print("[ERROR] Wrong depot specification. Please check.\nAborting...")
                exit(1)

            if demand != 0:
                print("[ERROR] Depot has a demand. Please check.\nAborting...")
                exit(1)

            depot = self.depots[depot_index]
            depot.customer_id = depot_customer_id
            depot.x, depot.y = x,y
            depot.service_time, depot.ready_time, depot.due_date = service, ready_time, due_date

            self.coordinates[depot_customer_id] = x,y
            depot_index += 1

        self.travel_times = self.distances = geometry.distances.calculate_distance_matrix(self.coordinates)


    def print_instance(self, debug=False):
        print("=================================== MDVRPTW INSTANCE ========================================")
        print(f"\n  Number of clients: {self.number_of_clients}"
              f"\n  Number of depots: {self.number_of_depots}")


        print("\n\nClients\n")
        print("ID\tX\tY\tDEMAND\t\tREADY TIME\tDUE DATE\tSERVICE\tTRAVEL TIME")
        for i in range(self.number_of_clients +1):
            client_id, x, y, demand, ready_time, due_date, service = i, self.coordinates[i][0], self.coordinates[i][1], self.demands[i], self.time_windows[i][0], self.time_windows[i][1], self.services[i]
            print("{}\t{}\t{}\t{}\t\t{}\t\t{}\t\t{}".format(client_id, x, y, demand, ready_time, due_date, service))


        print("\n\nDepots\n")
        for i in range(self.number_of_depots):
            depot = self.depots[i]
            print(f"{depot.customer_id}\t{depot.x}\t{depot.y}\t{0.0}\t\t{depot.ready_time}\t\t{depot.due_date}\t\t{depot.service_time}")
        print("===========================================================================================")


        if debug:
            print("\n  DISTANCE MATRIX ({}x{})". format(len(self.distances), len(self.distances[0])) )
            for i in range(self.number_of_clients):
                print(self.distances[i])

            print("\n  TRAVEL TIMES ({}x{})". format(len(self.distances), len(self.distances[0])) )
            for i in range(self.number_of_clients):
                print(self.travel_times[i])

            print("\n  TIME WINDOWS")
            print(self.time_windows)

            print("\n  SERVICE")
            print(self.services, "\n")