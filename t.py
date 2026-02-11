import numpy as np
import matplotlib.pyplot as plt

# 5.1 a)
L=100
x=np.random.normal(loc=0, scale=1,size=L)
samples= np.linspace(-4,4,100)
plt.hist(x,bins=10,density =True)
plt.plot(samples, 1/ np.sqrt (2* np.pi)*np.exp ( -.5* samples **2))
plt.show()

# b)
print(np.mean(x))
print(np.var(x))