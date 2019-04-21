import ast
import json
import yaml
import pickle
from sys import getsizeof
import math
import matplotlib.pyplot as plt


def distance(origin, destination):
    """
    Calculateaza distanta intre 2 puncte x(lat,long)
     """
    lat1, lon1 = origin
    lat2, lon2 = destination
    dist=math.sqrt((math.pow(abs(lat2-lat1),2))+math.pow(abs(lon2-lon1),2))

    return dist

def reading():
    with open('HartaTraseu.txt', 'r') as f:
        s = f.read()
        whip = ast.literal_eval(s)
    return s

dict=reading()
noduri=ast.literal_eval(dict)
NrNoduri=noduri["NOD"].__len__()
print("Numar Noduri {}".format(NrNoduri))
maxdist=0
maximum=0
minNod=0
MaxNod=1

for y in range(1,NrNoduri-1):
    for z in range(y+1, NrNoduri):
        maxdist = distance(noduri["NOD"][y]["COORDINATES"],noduri["NOD"][z]["COORDINATES"])  # Just use 'min' instead of 'max' for minimum.
        if(maximum<maxdist):
            minNod=y
            maxNod=z
            maximum=maxdist
print("Distanta Maxima {} este intre nodul {} si nodul {}".format(maximum,minNod,maxNod))

for y in range(1,NrNoduri):
    plt.plot([noduri["NOD"][y]["COORDINATES"][0]], [noduri["NOD"][y]["COORDINATES"][1]], 'ro')
  #  plt.annotate(str(noduri["NOD"][y]["NAME"]), xy=(noduri["NOD"][y]["COORDINATES"][0], noduri["NOD"][y]["COORDINATES"][1]))
plt.axis([0, 9, 0, 5.5])
plt.show()

