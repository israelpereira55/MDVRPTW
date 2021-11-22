import math
import numpy as np

def euclidian_distance(p1, p2):
    diff = p1[0] - p2[0], p1[1] - p2[1]
    return np.linalg.norm(diff)

def calculate_distance_matrix(coordinates):
    number_of_lines = len(coordinates)
    distances = np.zeros((number_of_lines, number_of_lines))

    for i in range(number_of_lines):
        #p1 = coordinates[i]
        p1 = coordinates[i]
        for j in range(i, number_of_lines):
            #p2 = coordinates[j]
            #distances[i][j] = distances[j][i] = euclidian_distance(p1, p2)
            p2 = coordinates[j]
            distances[i][j] = distances[j][i] = euclidian_distance(p1, p2)

    return distances