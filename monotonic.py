
import noise
import random
import math
import matplotlib.pyplot as plt

dim = 100

def monotonicFunc(order): #monotonically decreasing random
    #function, of order (-order).
    const = random.random()
    if order<=0:
        return (lambda x: float(const) )
    else:
        headFunc = lambda x: float(const)/float(x**order)
        tailFunc = monotonicFunc(order-1)
        return (lambda x: headFunc(x) + tailFunc(x))

xcoords = range(dim)
ycoords = range(dim)


plt.show()
            

