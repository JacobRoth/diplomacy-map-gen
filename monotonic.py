
import noise
import random
import math
import matplotlib.pyplot as plt

dim = 100
period = 50
sealevel = -0.3
offset = random.randint(0,100)
riderAmp = 0.2

xcoords = range(dim)
ycoords = range(dim)

for x in xcoords:
    for y in ycoords:
        n =  noise.snoise2(x/period,y/period,base=offset)+random.random()*riderAmp
        if n > sealevel:
            plt.plot(x,y,"go")
        else:
            pass

plt.show()
            

