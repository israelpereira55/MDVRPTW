import matplotlib.pyplot as plt
from sklearn import datasets
import pandas as pd
import numpy as np
from scipy.stats import kurtosis
import statistics


 
hl = [2.58, 0.00, 1.46, 1.52, 1.19, 3.54, 0.00, 0.34, 0.27, 2.22, 0.61, -0.61, 0.00, -0.20, 0.81, 0.11]
ift = [0.92, 0.05, 1.47, 5.07, 4.68, 7.56, 0.36, 2.55, 3.71, 6.15, 0.94, 1.45, 1.65, 0.73, 0.81, 1.80]
eu = [2.90, 9.51, 9.89, 9.94, 10.96, 8.91, 3.31, 8.08, 12.95, 16.24, 6.81, 19.08, 16.76, 35.74, 20.11, 33.37]
 
data = {'HLRH': {'pr01':hl[0], 'pr02':hl[1], 'pr03':hl[2], 'pr04':hl[3], 'pr05':hl[4], 'pr06':hl[5], 'pr07':hl[6], 'pr08':hl[7], 'pr09':hl[8], 'pr10':hl[9], 'pr13':hl[10], 'pr14':hl[11], 'pr16':hl[12], 'pr18':hl[13], 'pr19':hl[14], 'pr20':hl[15]},
        'IF': {'pr01':ift[0], 'pr02':ift[1], 'pr03':ift[2], 'pr04':ift[3], 'pr05':ift[4], 'pr06':ift[5], 'pr07':ift[6], 'pr08':ift[7], 'pr09':ift[8], 'pr10':ift[9], 'pr13':ift[10], 'pr14':ift[11], 'pr16':ift[12], 'pr18':ift[13], 'pr19':ift[14], 'pr20':ift[15]},
        'RGRASP+VND': {'pr01':eu[0], 'pr02':eu[1], 'pr03':eu[2], 'pr04':eu[3], 'pr05':eu[4], 'pr06':eu[5], 'pr07':eu[6], 'pr08':eu[7], 'pr09':eu[8], 'pr10':eu[9], 'pr13':eu[10], 'pr14':eu[11], 'pr16':eu[12], 'pr18':eu[13], 'pr19':eu[14], 'pr20':eu[15]}}

df = pd.DataFrame(data)
df.plot(kind='bar')
plt.ylabel('%Dev')
plt.yticks(rotation=90)
#plt.ylabel("(%Dev) ", rotation=0)

plt.xticks(rotation=90, ha='right')
plt.savefig('f1.png', bbox_inches='tight')
plt.show()


