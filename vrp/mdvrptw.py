import numpy as np
import math

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

    number_of_vehicles : int
    number_of_clients : int
    number_of_depots : int

    # clustered_clients


    def __init__(self, instance_file):
        self.read_instance(instance_file)

        #self.vrptw_subproblems = []
        return


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
        #self.distances = np.zeros((vertices_number, vertices_number))
        self.time_windows = np.zeros((self.number_of_clients +1,2))
        self.services = np.zeros((self.number_of_clients +1))
        self.demands = np.zeros((self.number_of_clients +1))
        self.depots = [None] * self.number_of_depots


        # Depots
        for i in range(self.number_of_depots):
            route_max_time, vehicle_max_load = (float(x) for x in lines[1+i].split())
            depot = Depot(index=i, route_max_time=route_max_time, vehicle_max_load=vehicle_max_load)
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


        self.travel_times = self.distances = self.calculate_distance_matrix(self.coordinates)


    def calculate_distance_matrix(self,coordinates, ro1=1, ro2=0):
        #number_of_lines,number_of_columns = coordinates.shape

        number_of_lines = len(coordinates)
        distances = np.zeros((number_of_lines, number_of_lines))
        #travel_times = np.zeros((number_of_lines, number_of_lines))

        for i in range(number_of_lines):
            x1,y1 = coordinates[i]
            for j in range(i, number_of_lines):
                x2,y2 = coordinates[j]
                distances[i][j] = distances[j][i] = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )

                #travel_times[i][j] = ro1 * distances[i][j] + ro2 * time_windows

        return distances


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
            #return vrptw_example


    # GIOSA, 2002
    # Article: New assignment algorithms for the multi-depot vehicle routing problem
    def create_cluster_by_urgencies(self):
        closest_depots_index = np.zeros((self.number_of_clients +1))
        for c in range(1, self.number_of_clients +1):

            lowest_distance = self.distances[c][self.depots[0].customer_id] #initiating with the distance of the first depot
            closest_depot_index = self.depots[0].index

            for i in range(self.number_of_depots):
                depot = self.depots[i]
                depot_id = depot.customer_id
                if self.distances[c][depot_id] < lowest_distance:
                    lowest_distance = self.distances[c][depot_id]
                    closest_depot_index = depot.index

            closest_depots_index[c] = closest_depot_index


        uc_list = np.zeros((self.number_of_clients, 2)) #uc list has only possible clients and does not include client 0.

        for c in range(1, self.number_of_clients +1):
            sumatory = 0
            for i in range(self.number_of_depots):
                depot_id = self.depots[i].customer_id
                sumatory += self.distances[c][depot_id]

            closest_depot_index = int(closest_depots_index[c])
            u_c = sumatory - self.distances[c][closest_depot_index]
            uc_list[c-1] = u_c, c #uc list has only possible clients and does not include client 0.

        #u_c_list.sort(key=itemgetter(0))
        uc_list_ordered = sorted(uc_list, key=lambda tup: tup[0], reverse=True)


        maximum_demands = np.zeros((self.number_of_depots))
        for i in range(self.number_of_depots):
            maximum_demands[i] = self.depots[i].vehicle_max_load * self.number_of_vehicles

        #clustered_clients = [[]] * self.number_of_depots
        clustered_clients = []
        for i in range(self.number_of_depots):
            clustered_clients.append([])
            clustered_clients[i].append(self.depots[i].customer_id)


        for i in range(len(uc_list_ordered)):
            customer_id = int(uc_list_ordered[i][1])
            closest_depot_index = int(closest_depots_index[customer_id])

            if self.demands[customer_id] <= maximum_demands[closest_depot_index]:
                clustered_clients[closest_depot_index].append(customer_id)
                maximum_demands[closest_depot_index] -= self.demands[customer_id]
            else:

                client_got_clusterized = False
                for i in range(self.number_of_depots):
                    if self.demands[customer_id] <= maximum_demands[i]: #it's just an if. It's better to re ask about closest_depot_index than using a double if for all iterations (if demand suport and if it's not closest depot id)
                        clustered_clients[i].append(customer_id)
                        maximum_demands[i] -= self.demands[customer_id]
                        client_got_clusterized = True
                        break

                    
                if not client_got_clusterized:
                    print("[WARN]: Could not cluster by urgencies.")
                    return None

        return clustered_clients



    '''
    def create_solution_clustering_by_urgencies(self):

        mdvrptw_solution = MDVRPTW_Solution()
        for i in range(self.number_of_depots):
            vrptw_subproblem = VRPTW(number_of_vertices = len(self.clustered_clients[i]))
            vrptw_subproblem.create_by_cluster(vrptw_index=i, clustered_clients=self.clustered_clients[i], depot=self.depots[i], mdvrptw=self)
            #vrptw_subproblem.print_instance()
            mdvrptw_solution.vrptw_subproblems.append(vrptw_subproblem)

            print("CLUSTER", i)
            print(self.clustered_clients[i])

        return mdvrptw_solution

    
    def create_vrptw_subproblems(self):

        #self.vrptw_subproblems = []
        for i in range(self.number_of_depots):
            vrptw_subproblem = VRPTW(number_of_vertices = len(self.clustered_clients[i]))
            vrptw_subproblem.create_by_cluster(vrptw_index=i, clustered_clients=self.clustered_clients[i], depot=self.depots[i], mdvrptw=self)
            #vrptw_subproblem.print_instance()
            self.vrptw_subproblems.append(vrptw_subproblem)

            print("CLUSTER", i)
            print(self.clustered_clients[i])
            #vrptw_subproblem.print_instance(debug=True)
            #exit(1)
    


    def construct_solution_with_solomon(self, alpha1, alpha2, mu, lambdaa, debug=False, debug_level2=False):
        
        vrptw_solutions = []
        for vrptw_subproblem in self.vrptw_subproblems:
            vrptw_solution = solomon.insertion_heuristic(vrptw_subproblem, alpha1, alpha2, mu, lambdaa, debug, debug_level2)
            vrptw_solutions.append(vrptw_solution)

            #print(vrptw_solution.routes)
            #exit(1)

        return vrptw_solutions
    '''

