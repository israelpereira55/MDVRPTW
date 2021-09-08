import numpy as np
from matplotlib import pyplot

from sklearn.datasets import make_classification
from sklearn.cluster import Birch

from vrp import plot


def get_initial_depots(mdvrptw):
    depots = np.empty((mdvrptw.number_of_depots, 2))
    for i in range(mdvrptw.number_of_depots):
        depots[i] = mdvrptw.depots[i].x, mdvrptw.depots[i].y

    return depots


def get_depot_clusters_from_scikitlearn(mdvrptw, model):
    distances = np.zeros((mdvrptw.number_of_depots, mdvrptw.number_of_depots))
    depot_is_alocated = [False] * mdvrptw.number_of_depots
    cluster_is_allocated = [False] * mdvrptw.number_of_depots

    clustered_depots = []
    for i in range(mdvrptw.number_of_depots):
        clustered_depots.append([])
        #clustered_depots[i].append(0)

    #Scikit learn cluster i x MDVRPTW depot j
    for i in range(mdvrptw.number_of_depots):
        p1 = model.subcluster_centers_[i]
        for j in range(mdvrptw.number_of_depots):
            p2 = mdvrptw.depots[j].x, mdvrptw.depots[j].y
            distances[i][j] = np.linalg.norm(p1-p2)

    number_of_allocated_depots = 0
    while number_of_allocated_depots < mdvrptw.number_of_depots:
        lowest = 1000000
        lowest_index = -1,-1
        for j in range(mdvrptw.number_of_depots): #j is the depot and i is the cluster
            if depot_is_alocated[j]:
                continue

            for i in range(mdvrptw.number_of_depots):
                if cluster_is_allocated[i]:
                    continue

                if lowest > distances[i][j]:
                    lowest = distances[i][j]
                    lowest_index = i,j

        nearest_depot = lowest_index[1] #j
        cluster = lowest_index[0] #i
        clustered_depots[cluster].append(mdvrptw.depots[nearest_depot].customer_id)
        depot_is_alocated[nearest_depot] = True
        cluster_is_allocated[cluster] = True
        number_of_allocated_depots += 1


    print(clustered_depots)
    return clustered_depots


def get_distances_client_to_depots(client, free_capacities, mdvrptw):
    distances = np.zeros((mdvrptw.number_of_depots))
    MAX = 1000000
    for depot_index in range(mdvrptw.number_of_depots):
        if free_capacities[depot_index] >= mdvrptw.demands[client]:
            p1 = mdvrptw.coordinates[client]
            p2 = mdvrptw.depots[depot_index].x, mdvrptw.depots[depot_index].y
            distances[depot_index] = np.linalg.norm(p1-p2)
        else:
            distances = MAX

    return distances


def clusterize_by_scikitlearn(mdvrptw, model, check_demand=True, show_test=False, show_warns=False):
    X = mdvrptw.coordinates[1:mdvrptw.number_of_clients+1] #client of index 0 is nothing on the mdvrptw instance
    model.fit(X)
    #prediction = model.fit_predict(X)
    prediction = model.predict(X)


    clustered_clients = []
    for i in range(mdvrptw.number_of_depots):
        clustered_clients.append([mdvrptw.depots[i].customer_id])

    if check_demand:
        free_capacities = np.zeros((mdvrptw.number_of_depots))

        for i in range(mdvrptw.number_of_depots):
            free_capacities[i] = mdvrptw.number_of_vehicles * mdvrptw.depots[i].vehicle_max_load
        
        #Clients start on index 1, but prediction start on index 0
        # So prediction 1 predicts client 2.
        for i in range(1, mdvrptw.number_of_clients +1):
            depot = prediction[i-1]
            if free_capacities[depot] >= mdvrptw.demands[i]:
                clustered_clients[depot].append(i)
            else:
                distances = get_distances_client_to_depots(i, free_capacities, mdvrptw)
                if show_warns: print("[WARN]: Out of demands, finding another depot to clusterize.")
                
                dist, index = min((dist, index) for (index, dist) in enumerate(distances))
                clustered_clients[index].append(i)
    else:
        #Clients start on index 1, but prediction start on index 0
        # So prediction 1 predicts client 2.
        for i in range(1, mdvrptw.number_of_clients +1):
            clustered_clients[prediction[i-1]].append(i)


    # Validating:
    sumatory = 0
    for clustered_depot in clustered_clients:
        sumatory += len(clustered_depot)
    
    if show_test:
        for clustered_depot in clustered_clients:
            print(f"Depot size:{len(clustered_depot)}", clustered_depot)
        print("Number of clients:", sumatory)

    if sumatory != mdvrptw.number_of_clients + mdvrptw.number_of_depots:
        print("[ERROR]: The clusterization results seems to be incomplete.\nAborting...")
        exit(1)

    return clustered_clients



def clusterize_by_scikitlearn_ordering_depots(mdvrptw, model, check_demand=True, show_test=False, show_warns=False):
    X = mdvrptw.coordinates[1:mdvrptw.number_of_clients+1] #client of index 0 is nothing on the mdvrptw instance
    #model.fit(X)
    #prediction = model.predict(X)
    prediction = model.fit_predict(X)

    clustered_clients = get_depot_clusters_from_scikitlearn(mdvrptw, model)

    if check_demand:
        free_capacities = np.zeros((mdvrptw.number_of_depots))

        for i in range(mdvrptw.number_of_depots):
            free_capacities[i] = mdvrptw.number_of_vehicles * mdvrptw.depots[i].vehicle_max_load
        
        #Clients start on index 1, but prediction start on index 0
        # So prediction 1 predicts client 2.
        for i in range(1, mdvrptw.number_of_clients +1):
            depot = prediction[i-1]
            if free_capacities[depot] >= mdvrptw.demands[i]:
                clustered_clients[depot].append(i)
            else:
                distances = get_distances_client_to_depots(i, free_capacities, mdvrptw)
                if show_warns: print("[WARN]: Out of demands, finding another depot to clusterize.")
                
                dist, index = min((dist, index) for (index, dist) in enumerate(distances))
                clustered_clients[index].append(i)
    else:
        #Clients start on index 1, but prediction start on index 0
        # So prediction 1 predicts client 2.
        for i in range(1, mdvrptw.number_of_clients +1):
            clustered_clients[prediction[i-1]].append(i)

    #Ordering depots on clusters
    ordered_clustered_clients = []
    for i in range(mdvrptw.number_of_depots):
        ordered_clustered_clients.append([])

    for i in range(mdvrptw.number_of_depots):
        depot = clustered_clients[i][0]
        ordered_clustered_clients[depot - mdvrptw.number_of_clients -1] = clustered_clients[i]
    
    clustered_clients = ordered_clustered_clients

    # Validating:
    sumatory = 0
    for clustered_depot in clustered_clients:
        sumatory += len(clustered_depot)
    
    if show_test:
        for clustered_depot in clustered_clients:
            print(f"Depot size:{len(clustered_depot)}", clustered_depot)
        print("Number of clients:", sumatory)

    if sumatory != mdvrptw.number_of_clients + mdvrptw.number_of_depots:
        print("[ERROR]: The clusterization results seems to be incomplete.\nAborting...")
        exit(1)

    return clustered_clients

# GIOSA, 2002
# Article: New assignment algorithms for the multi-depot vehicle routing problem
def clusterize_by_urgencies(mdvrptw, show_test=False):
    closest_depots_index = np.zeros((mdvrptw.number_of_clients +1))
    for c in range(1, mdvrptw.number_of_clients +1):

        lowest_distance = mdvrptw.distances[c][mdvrptw.depots[0].customer_id] #initiating with the distance of the first depot
        closest_depot_index = mdvrptw.depots[0].index

        for i in range(mdvrptw.number_of_depots):
            depot = mdvrptw.depots[i]
            depot_id = depot.customer_id
            if mdvrptw.distances[c][depot_id] < lowest_distance:
                lowest_distance = mdvrptw.distances[c][depot_id]
                closest_depot_index = depot.index

        closest_depots_index[c] = closest_depot_index


    uc_list = np.zeros((mdvrptw.number_of_clients, 2)) #uc list has only possible clients and does not include client 0.

    for c in range(1, mdvrptw.number_of_clients +1):
        sumatory = 0
        for i in range(mdvrptw.number_of_depots):
            depot_id = mdvrptw.depots[i].customer_id
            sumatory += mdvrptw.distances[c][depot_id]

        closest_depot_index = int(closest_depots_index[c])
        u_c = sumatory - mdvrptw.distances[c][closest_depot_index]
        uc_list[c-1] = u_c, c #uc list has only possible clients and does not include client 0.

    #u_c_list.sort(key=itemgetter(0))
    uc_list_ordered = sorted(uc_list, key=lambda tup: tup[0], reverse=True)


    maximum_demands = np.zeros((mdvrptw.number_of_depots))
    for i in range(mdvrptw.number_of_depots):
        maximum_demands[i] = mdvrptw.depots[i].vehicle_max_load * mdvrptw.number_of_vehicles

    #clustered_clients = [[]] * mdvrptw.number_of_depots
    clustered_clients = []
    for i in range(mdvrptw.number_of_depots):
        clustered_clients.append([])
        clustered_clients[i].append(mdvrptw.depots[i].customer_id)


    for i in range(len(uc_list_ordered)):
        customer_id = int(uc_list_ordered[i][1])
        closest_depot_index = int(closest_depots_index[customer_id])

        if mdvrptw.demands[customer_id] <= maximum_demands[closest_depot_index]:
            clustered_clients[closest_depot_index].append(customer_id)
            maximum_demands[closest_depot_index] -= mdvrptw.demands[customer_id]
        else:

            client_got_clusterized = False
            for i in range(mdvrptw.number_of_depots):
                if mdvrptw.demands[customer_id] <= maximum_demands[i]: #it's just an if. It's better to re ask about closest_depot_index than using a double if for all iterations (if demand suport and if it's not closest depot id)
                    clustered_clients[i].append(customer_id)
                    maximum_demands[i] -= mdvrptw.demands[customer_id]
                    client_got_clusterized = True
                    break

            if not client_got_clusterized:
                print("[ERROR]: Could not cluster by urgencies.\nAborting...")
                exit(1)

    # Validating:
    sumatory = 0
    for clustered_depot in clustered_clients:
        sumatory += len(clustered_depot)
    
    if show_test:
        for clustered_depot in clustered_clients:
            print(f"Depot size:{len(clustered_depot)}", clustered_depot)
        print("Number of clients:", sumatory)

    if sumatory != mdvrptw.number_of_clients + mdvrptw.number_of_depots:
        print("[ERROR]: The clusterization results seems to be incomplete.\nAborting...")
        exit(1)

    return clustered_clients