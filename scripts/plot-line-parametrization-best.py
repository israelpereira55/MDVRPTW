import math
import matplotlib.pyplot as plt
import numpy as np
 
#plt.title('n={}'.format(n))
#plt.plot(x_axis, probs, 'o', label='binomial', color='black');

kmeans_ctw = [2792.03, 2746.01, 2770.40, 2778.35, 2777.13, 2786.66, 2743.89, 2748.34, 2748.20, 2718.57, 2713.20]
kmeans_fa = [2776.39, 2783.63, 2754.21, 2767.68, 2757.52, 2753.21, 2737.72, 2710.94, 2727.60, 2727.32, 2639.89]

#urgencies_ctw = [2193.22, 2190.15, 2172.43, 2205.54, 2169.23, 2173.80, 2198.18, 2159.59, 2148.70, 2173.41, 2183.04]
urgencies_fa = [2806.09, 2779.21, 2796.23, 2780.23, 2776.55, 2751.35, 2750.46, 2695.45, 2721.14, 2699.28, 2678.19]

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
plt.ylabel('Best of 10 runs')


plt.xticks(x, labels, rotation='horizontal')
plt.legend(loc="lower left")
#plt.legend(bbox_to_anchor=(1, 1), loc='upper right', ncol=1)
#plt.legend(bbox_to_anchor=(1,1), loc="upper left", ncol=1)
#plt.legend(bbox_to_anchor=(1, 1.25), loc='upper left', ncol=1)
fig.savefig('best.png', bbox_inches='tight')
plt.show()

