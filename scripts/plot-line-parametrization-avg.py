import math
import matplotlib.pyplot as plt
import numpy as np
 
#plt.title('n={}'.format(n))
#plt.plot(x_axis, probs, 'o', label='binomial', color='black');

kmeans_ctw = [2867.09, 2844.35, 2856.14, 2863.37, 2837.54, 2835.38, 2828.81, 2841.09, 2838.91, 2790.61, 2799.37]
kmeans_fa = [2860.54, 2853.42, 2837.03, 2845.59, 2830.44, 2814.13, 2809.64, 2792.72, 2786.90, 2762.58, 2731.40]

#urgencies_ctw = [2237.53, 2255.14, 2251.77, 2248.08, 2220.15, 2216.99, 2252.71, 2226.29, 2233.49, 2234.61, 2235.50]
urgencies_fa = [2857.08, 2884.95, 2863.56, 2871.09, 2856.87, 2841.26, 2831.73, 2801.42, 2807.41, 2760.08, 2763.37]

#x = ['r_0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r11']
x = [0,1,2,3,4,5,6,7,8,9,10]
x2 = [0,1,2,3,4,5,6,7,8,9]

fig = plt.figure(1)
labels = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10']
plt.plot(x, kmeans_fa, label='KMeans FC', color='red');
plt.plot(x, kmeans_ctw, label='KMeans CTW', color='blue');
#plt.plot(x2, urgencies_fa, label='Urgencies FA', color='orange');
plt.plot(x, urgencies_fa, label='Urgencies FC', color='orange');
#plt.plot(x, urgencies_ctw, label='Urgencies CTW', color='cyan');

plt.xlabel('Solomon Insertion heuristic I1 strategy')
plt.ylabel('Average of 10 runs')

plt.xticks(x, labels, rotation='horizontal')
plt.legend(loc="lower left")
#plt.legend(bbox_to_anchor=(1, 1), loc='upper right', ncol=1)
#plt.legend(bbox_to_anchor=(1,1), loc="upper left", ncol=1)
#plt.legend(bbox_to_anchor=(1, 1.25), loc='upper left', ncol=1)
fig.savefig('avg.png', bbox_inches='tight')
plt.show()

