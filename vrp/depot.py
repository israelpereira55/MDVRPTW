'''
    Depot Class

        * On this problem, the number of vehicles is the same for all depots. 
          So this number is stored on MDVRPTW.
'''

class Depot:
    index : int             # can be 1 to number of depots
    customer_id : int       # the customer number from the instance
    route_max_time : int
    vehicle_max_load : int

    x : float               # 2D coordinates 
    y : float
    service_time : float
    ready_time : float      # earliest time of service
    due_date   : float      # latest time of service

    def __init__(self, index, route_max_time, vehicle_max_load):
        self.index = index
        self.route_max_time = route_max_time
        self.vehicle_max_load = vehicle_max_load

        self.customer_id = 0
        self.x = self.y = self.service_time = self.ready_time = self.due_date = 0.0
        