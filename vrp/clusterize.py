import math
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
            free_capacities[i] = mdvrptw.number_of_vehicles * mdvrptw.depots[i].vehicle_capacity
        
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
            free_capacities[i] = mdvrptw.number_of_vehicles * mdvrptw.depots[i].vehicle_capacity
        
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
        maximum_demands[i] = mdvrptw.depots[i].vehicle_capacity * mdvrptw.number_of_vehicles

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



# 3C clusterization
def get_average_distance_client_to_cluster(mdvrptw, city, cluster):
    distances = 0
    for ci in cluster:
        distances += mdvrptw.distances[city][ci]

    return distances/(len(cluster)+1) #TODO VERIFICAR +1

# 3C clusterization
def get_two_closest_clusters(mdvrptw, city, clusters):
    c0 = clusters[0][0]
    cost = mdvrptw.distances[city][c0]
    best_index = 0

    for index in range(1, len(clusters)):
        c0 = clusters[index][0]
        new_cost = mdvrptw.distances[city][c0]
        if new_cost < cost:
            cost = new_cost
            best_index = index

    closest_cluster = best_index


    if closest_cluster != 0:
        c0 = clusters[0][0]
        best_index = 0
    else:
        c0 = clusters[1][0]
        best_index = 1

    cost = mdvrptw.distances[city][c0]

    for index in range(len(clusters)):
        if index == closest_cluster or index == best_index:
            continue

        c0 = clusters[index][0]
        new_cost = mdvrptw.distances[city][c0]
        if new_cost < cost:
            cost = new_cost
            best_index = index

    second_cluster = best_index
    return closest_cluster, second_cluster #indexers

#3C clusterization
def get_variance_of_avg_distance(mdvrptw, client, cluster, avg_distance):
    #avg_distance = get_average_distance_client_to_cluster(mdvrptw, client, cluster)
    variance = 0
    for ci in cluster:
        dist = mdvrptw.distances[client][ci]
        variance += (dist - avg_distance) * (dist - avg_distance)

    return variance / (len(cluster)) #TODO CHECK SE FAZ N-1

def three_criteria_clustering(mdvrptw, show_test=False):
    clusters = []
    for i in range(mdvrptw.number_of_clients+1, mdvrptw.number_of_clients+mdvrptw.number_of_depots+1):
        clusters.append([i])

    unclustered_clients = [0] * mdvrptw.number_of_clients
    for i in range(mdvrptw.number_of_clients):
        unclustered_clients[i] = i+1

    clients_closest_cluster = [-1] * (mdvrptw.number_of_clients +1)
    clients_second_cluster = [-1] * (mdvrptw.number_of_clients +1)
    for client in unclustered_clients:
        closest_cluster, second_cluster = get_two_closest_clusters(mdvrptw, client, clusters)
        clients_closest_cluster[client] = closest_cluster
        clients_second_cluster[client] = second_cluster


    #indexers = [None] * (mdvrptw.number_of_clients+1)
    number_of_clustered_clients = 0
    while number_of_clustered_clients < mdvrptw.number_of_clients:

        avg_distances = np.zeros((mdvrptw.number_of_clients+1, 3), dtype=int) # for each client, it stores the avg. distances to the first and second closest depot and the client index of the unclustered list
        differences = np.zeros((mdvrptw.number_of_clients+1))
        for index, client in enumerate(unclustered_clients):
            avg_distances[client][0] = get_average_distance_client_to_cluster(mdvrptw, client, clusters[clients_closest_cluster[client]])
            avg_distances[client][1] = get_average_distance_client_to_cluster(mdvrptw, client, clusters[clients_second_cluster[client]])    
            avg_distances[client][2] = index
            differences[client] = abs(avg_distances[client][0] - avg_distances[client][1])

        max_idx = np.argmax(differences) #or max() if not np.
        max_difference = differences[max_idx]
        index = avg_distances[max_idx][2]

        highest_avg_distance = avg_distances[max_idx][0] if avg_distances[max_idx][0] > avg_distances[max_idx][1] else avg_distances[max_idx][1]
        if max_difference >= 0.1*highest_avg_distance:
            closest_cluster = clients_closest_cluster[max_idx]
            clusters[closest_cluster].append(max_idx)
            unclustered_clients.pop(index)
            number_of_clustered_clients += 1
            continue

        else: # SECOND CRITERIA (VARIANCE)
            
            indexers = np.zeros((mdvrptw.number_of_clients+1), dtype=int) #client index of unclustered clients list
            variances = np.full((mdvrptw.number_of_clients+1), fill_value=float('inf')) 
            for index, client in enumerate(unclustered_clients):
                variances[client] = get_variance_of_avg_distance(mdvrptw, client, clusters[clients_closest_cluster[client]], avg_distances[client][0])
                indexers[client] = index

            min_idx = np.argmin(variances)
            min_variance = variances[min_idx]
            index = indexers[min_idx]

            if min_variance <= 0.4*avg_distances[min_idx][0]:
                closest_cluster = clients_closest_cluster[min_idx]
                clusters[closest_cluster].append(min_idx)
                unclustered_clients.pop(index)
                number_of_clustered_clients += 1
                continue

                #TODO FALTA POP, PEGA O ID EM CIMA
            else: #THIRD CRITERIA (CRUDE DISTANCE TO CLUSTER)

                distances = np.full((mdvrptw.number_of_clients+1), fill_value=float('inf'))
                indexers = np.zeros((mdvrptw.number_of_clients+1), dtype=int) #client index of unclustered clients list

                for index,client in enumerate(unclustered_clients):
                    closest_cluster = clients_closest_cluster[client]
                    distances[client] = mdvrptw.distances[client][closest_cluster]
                    indexers[client] = index

                min_idx = np.argmin(distances)
                min_distance = distances[min_idx]
                index = indexers[min_idx]


                #Assignment
                closest_cluster = clients_closest_cluster[min_idx]
                clusters[closest_cluster].append(min_idx)
                unclustered_clients.pop(index)
                number_of_clustered_clients += 1
                continue

    #TODO: AGR CORRIGIR SE A DEMANDA PASSOU, jogando os ultimos pra o proximo cluster mais prox q suporte
    free_capacities = np.zeros((mdvrptw.number_of_depots))
    for i in range(mdvrptw.number_of_depots):
        free_capacities[i] = mdvrptw.number_of_vehicles * mdvrptw.depots[i].vehicle_capacity

    for index, cluster in enumerate(clusters):
        for ci in range(1, len(cluster)):
            free_capacities[index] -= mdvrptw.demands[ci]

    for index in range(len(free_capacities)):
        if free_capacities[index] < 0:
            print('precisa implementar a demanda da clusterizacao') #TODO chuta os ultimos pros clusters mais prox que suportem
            exit(1)

    #print(clusters)
    return clusters

# Common functions
def get_closest_depots_index(mdvrptw):
    closest_depots_index = np.zeros((mdvrptw.number_of_clients +1), dtype=int)

    for ci in range(1, mdvrptw.number_of_clients +1):

        lowest_distance = mdvrptw.distances[ci][mdvrptw.depots[0].customer_id] #initiating with the distance of the first depot
        closest_depot_index = mdvrptw.depots[0].index

        for i in range(mdvrptw.number_of_depots):
            depot = mdvrptw.depots[i]
            depot_id = depot.customer_id
            if mdvrptw.distances[ci][depot_id] < lowest_distance:
                lowest_distance = mdvrptw.distances[ci][depot_id]
                closest_depot_index = depot.index

        closest_depots_index[ci] = closest_depot_index

    return closest_depots_index


# Article: New measures of proximity for the assignment algorithms in the MDVRPTW
# Partial requirement
# Note: We use [ei, li] as the earliest time of service (ei) and latest time of service (li) as defined on the classicals VRPTW/MDVRPTW formulations.
def distance_time_windows(ei, li, ej, lj):
    if   ei < lj:
        return lj - ei
    elif ej < li:
        return li - ej
    else:
        return 0

# Article: New measures of proximity for the assignment algorithms in the MDVRPTW
# Partial requirement
def calculate_affinity(mdvrptw, ci, cluster):
    d = cluster[0] - mdvrptw.number_of_clients -1
    depot = mdvrptw.depots[d]
    affinity = math.e ** -(distance_time_windows(*mdvrptw.time_windows[ci], depot.ready_time, depot.due_date) + mdvrptw.travel_times[ci][cluster[0]])

    for j in range(1, len(cluster)):
        cj = cluster[j]
        affinity += math.e ** -(distance_time_windows(*mdvrptw.time_windows[ci], *mdvrptw.time_windows[cj]) + mdvrptw.travel_times[ci][cj])
    return affinity

# L Tansini and O Viera, 2006
# Article: New measures of proximity for the assignment algorithms in the MDVRPTW
# Urgencies with parallel approach implemented using the new measures
def clusterize_by_closeness(mdvrptw, show_test=False):
    closest_depots_index = get_closest_depots_index(mdvrptw)

    # Calculating affinity
    clustered_clients = []
    for i in range(mdvrptw.number_of_depots):
        clustered_clients.append([])
        clustered_clients[i].append(mdvrptw.depots[i].customer_id)

    maximum_demands = np.zeros((mdvrptw.number_of_depots))
    current_demands = np.zeros((mdvrptw.number_of_depots))
    for i in range(mdvrptw.number_of_depots):
        maximum_demands[i] = mdvrptw.depots[i].vehicle_capacity * mdvrptw.number_of_vehicles

    is_client_clustered = np.zeros((mdvrptw.number_of_clients +1))
    #closenesses = np.zeros((mdvrptw.number_of_clients+1)) #TODO
    closenesses = [0] * (mdvrptw.number_of_clients+1)

    for number_of_routed_clients in range(1, mdvrptw.number_of_clients+1):
        for ci in range(1, mdvrptw.number_of_clients+1):
            closenesses[ci] = 0 # If the client is already clustered, its urgency is kept as 0.
            if is_client_clustered[ci]:
                continue

            for d in range(mdvrptw.number_of_depots):
                if closest_depots_index[ci] == d:
                    continue

                cluster = clustered_clients[d]
                cj = mdvrptw.depots[d].customer_id
                closenesses[ci] += mdvrptw.distances[ci][cj] / calculate_affinity(mdvrptw, ci, cluster)
            
            d = closest_depots_index[ci]
            cluster = clustered_clients[d]
            cj = mdvrptw.depots[d].customer_id
            closenesses[ci] -= mdvrptw.distances[ci][cj] / calculate_affinity(mdvrptw, ci, cluster)

        max_value = max(closenesses)
        max_index = closenesses.index(max_value)

        client = max_index
        d = closest_depots_index[client]
        demand = mdvrptw.mdvrp.demands[ci]

        if current_demands[d] + demand > maximum_demands[d]:
            #Finding the second closest depot that has free demand to allow it, so, we will be changing d.
            lowest_distance = float('inf')
            closest_depot_index = -1
            for d in range(mdvrptw.number_of_depots):

                if d == closest_depots_index[client]: #TODO CHEEEEECK
                    continue

                depot = mdvrptw.depots[d]
                depot_id = depot.customer_id
                if (mdvrptw.distances[client][depot_id] < lowest_distance) and (current_demands[d] + demand <= maximum_demands[d]):
                    lowest_distance = mdvrptw.distances[client][depot_id]
                    closest_depot_index = d 

            if closest_depot_index == -1:
                print("[ERROR]: The clusterization could not complete.\nAborting...")
                exit(1)
            d = closest_depots_index

        # On every iteration, a client will be appended to a depot.
        clustered_clients[d].append(client)
        current_demands[d] += demand

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