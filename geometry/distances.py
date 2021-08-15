import math
import numpy as np

def calculate_distance_matrix(coordinates):
    number_of_lines = len(coordinates)
    distances = np.zeros((number_of_lines, number_of_lines))

    for i in range(number_of_lines):
        x1,y1 = coordinates[i]
        for j in range(i, number_of_lines):
            x2,y2 = coordinates[j]
            distances[i][j] = distances[j][i] = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )

    return distances