import numpy as np
import matplotlib.pyplot as plt

def pi(x):
    if(x < 0):
        return 1/((10+np.abs(x))**4)
    if(x < 1):
        return 0.9
    if(x < 2):
        return 0.1
    if(2 <= x):
        return 1/((10+np.abs(x))**4)

def q(x):
    return np.random.normal(x,1)

def q_pdf(x_prev,x):
    mu=x_prev
    sigma2=1**2
    return 1/(np.sqrt(2*np.pi*sigma2))*np.exp(-0.5*((x-mu)**2)/sigma2)

L=10000
x_0 = -100
x=x_0
x_sample=np.zeros(L+1)

accepted=0
for n in range(L):
    x_prim= q(x)

    a= (pi(x_prim)*q_pdf(x,x_prim))/(pi(x)*q_pdf(x_prim,x))
    
    if(np.random.uniform(0,1)<a):
        x= x_prim
        accepted+=1
    x_sample[n+1]=x

sample = np. linspace (0, L, L+1)
burn_in=0
print("Acceptance rate: "+str( accepted /L))

# plt.plot(x_sample[burn_in:])
# plt.show ()

# plt. scatter (sample[burn_in:], x_sample)
# plt.show ()

# plt.hist( x_sample[burn_in:], bins =20)
# plt.show ()