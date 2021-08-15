import numpy as np
import math


class VRPTW:
    #coordinates   [x,y]   
    #distances      dij     distance matrix
    #time_windows  [ei, li] earliest time of service, latest time of service 
    #services      [si]     service time 
    #demands       [?] 

    vehicle_capacity : int
    number_of_vehicles : int
    number_of_clients : int

    is_initiated = False
    #clustered_clients

    def __init__(self, number_of_vertices): # +1 for depot
        self.coordinates = np.zeros((number_of_vertices,2))
        self.distances = np.zeros((number_of_vertices, number_of_vertices))
        self.time_windows = np.zeros((number_of_vertices,2))
        self.services = np.zeros((number_of_vertices))
        self.demands = np.zeros((number_of_vertices))

        self.number_of_clients = number_of_vertices -1 #depot
        self.number_of_vehicles = 0
        self.vehicle_capacity = 0

        self.clustered_clients = None
        self.depot = None
        self.index = -1

    '''
    def read_instance(self, instance_file):
        try:
            file = open(instance_file)
            lines =  file.readlines()[4:]
            file.close()
        except IOError:
            print("[ERROR]: Could not open the {} file.".format(instance_file))
            exit(1)


        self.number_of_vehicles, self.vehicle_capacity = (int(x) for x in lines[0].split())
        #print(number_of_vehicles, vehicle_capacity)

        for i in range(self.number_of_clients):
            line = lines[5 + i]

            #print(line[:len(line) -1])
            client_id, x, y, demand, ready_time, due_date, service = [int(x) for x in line.split()]

            self.coordinates[i] = x,y
            self.time_windows[i] = ready_time, due_date
            self.services[i] = service
            self.demands[i] = demand

        self.travel_times = self.distances = self.calculate_distance_matrix(self.coordinates)
    '''

    def create_by_cluster(self, vrptw_index, clustered_clients, depot, mdvrptw):
        self.is_initiated = True
        self.number_of_vehicles, self.vehicle_capacity = mdvrptw.number_of_vehicles, depot.vehicle_max_load

        if self.number_of_clients +1 != len(clustered_clients):
            print("[ERROR]: Number of clients of VRPTW instance differs than the number of clustered clients.")
            exit(1)

        self.depot = depot
        self.index = vrptw_index
        
        #0 is the depot
        self.coordinates[0] = depot.x, depot.y
        self.time_windows[0] = depot.ready_time, depot.due_date
        self.services[0] = depot.service_time
        self.demands[0] = 0.0

        #self.number_of_clients += 1
        
        
        customer_id = 1
        for i in range(1, self.number_of_clients +1):
            customer = clustered_clients[i]
            self.coordinates[customer_id] = mdvrptw.coordinates[customer]
            self.time_windows[customer_id] = mdvrptw.time_windows[customer]
            self.services[customer_id] = mdvrptw.services[customer]
            self.demands[customer_id] = mdvrptw.demands[customer]

            customer_id +=1
        
        '''
        index = 0
        for vertice in clustered_clients: # also has the depot
            self.coordinates[index] = mdvrptw.coordinates[vertice]
            self.time_windows[index] = mdvrptw.time_windows[vertice]
            self.services[index] = mdvrptw.services[vertice]
            self.demands[index] = mdvrptw.demands[vertice]

            index +=1
        '''

        self.travel_times = self.distances = self.calculate_distance_matrix(self.coordinates)
        self.clustered_clients = clustered_clients



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

    #def calculate_travel_time


    def create_renatos_example(self,):
        self.distances = [ [ 0,28,31,20,25,34],
                                           [28, 0,21,29,26,20],
                                           [31,21, 0,38,20,32],
                                           [20,29,38, 0,30,27],
                                           [25,26,20,30, 0,25],
                                           [34,20,32,27,25, 0]
                                         ]

        self.time_windows = [ [0,1000],
                                            [2,5],
                                            [4,6],
                                            [2,3],
                                            [5,8],
                                            [0,3]
                                          ]

        self.travel_times = [ [ 0, 2, 3, 1, 2, 3],
                                          [ 2, 0, 1, 2, 2, 1],
                                          [ 3, 2, 0, 4, 1, 3],
                                          [ 1, 2, 4, 0, 3, 2],
                                          [ 2, 2, 1, 3, 0, 2],
                                          [ 3, 1, 3, 2, 2, 0]
                                        ]

        self.services = [0, 3, 2, 4, 1, 4]
        self.demands =  [ 0,37,35,30,25,32]

        self.number_of_vehicles = 25
        self.vehicle_capacity = 100


    def print_instance(self, debug=False):
        vertices_number = self.number_of_clients +1 #depot
        print("=================================== VRPTW INSTANCE ========================================")

        print("ID\tX\tY\tDEMAND\t\tREADY TIME\tDUE DATE\tSERVICE\tTRAVEL TIME")
        for i in range(vertices_number):
            client_id, x, y, demand, ready_time, due_date, service = i, self.coordinates[i][0], self.coordinates[i][1], self.demands[i], self.time_windows[i][0], self.time_windows[i][1], self.services[i]
            print("{}\t{}\t{}\t{}\t\t{}\t\t{}\t\t{}".format(client_id, x, y, demand, ready_time, due_date, service))
        print("===========================================================================================")


        if debug:
            print("\n  DISTANCE MATRIX ({}x{})". format(len(self.distances), len(self.distances[0])) )
            for i in range(vertices_number):
                print(self.distances[i])

            print("\n  TRAVEL TIMES ({}x{})". format(len(self.distances), len(self.distances[0])) )
            for i in range(vertices_number):
                print(self.travel_times[i])

            print("\n  TIME WINDOWS")
            print(self.time_windows)

            print("\n  SERVICE")
            print(self.services, "\n")
            #return vrptw_example


