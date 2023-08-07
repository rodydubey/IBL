import xml.etree.ElementTree as ET
from sumolib import checkBinary
import os
import sys
import numpy as np
import traci
import csv
from sumolib import net
import json

def getEdgesBetweenOD(network):
    
    fromEdgeArray = [-840,-1797,-1404,-1891,-621,-1882,-1201]
    ToEdgeArray = [496,867,1483,1404,1464,601,686]
    itr = 0
    bigList = []
    while itr < len(fromEdgeArray):
        fromEdge = network.getEdge(str(fromEdgeArray[itr]))
        toEdge = network.getEdge(str(ToEdgeArray[itr]))
        tuple1, tuple2 = network.getOptimalPath(fromEdge,toEdge)
        edgeList = []
        for tuple in tuple1:
            # print(tuple)
            keywords = 'id='
            before, _, after = str(tuple).partition(keywords)
            # print(before.split()[-1])
            tempText = after.split()[0]
            result = tempText.replace('"', "")
            edgeList.append(result)
        bigList.append(edgeList)
        itr+=1
    json_string = json.dumps(bigList)
    with open('../sumo_config/Routes.json', 'w') as outfile:
        outfile.write(json_string)
