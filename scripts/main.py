import numpy as np
import os, sys
from addLoopDetectors import loopDetector
from generateGraph import generateGraph
from utils import getEdgesBetweenOD
from sumolib import net

from writeActivityGenSupportingData import writeActivityGenSupportingData
"""
Configure various parameters of SUMO
"""

loopDetectorFileName = "../sumo_config/loopDetectors.add.xml"
networkFileName = '../sumo_config/SimpleRandom.net.xml'

# traci.start([sumoBinary] + sumoCMD)
step = 0
edge_list = [] # list of all edges

network = net.readNet(networkFileName)

nEdges = [e.getID() for e in network.getEdges()]

# Write additional file with loop detectors if the file does not exist
for edge_id in nEdges:   
    if edge_id.find("_") == -1: # filters edges from internal edges
        edge_list.append(edge_id)

###uncomment below function everytime you need to generate new Loop  detector additional file
loopDetector(network, edge_list, loopDetectorFileName)
###uncomment below function everytime you need to generate new Loop  detector additional file

getEdgesBetweenOD(network)

###uncomment below function everytime you need to generate new activityGen related files 
writeActivityGenSupportingData(networkFileName,edge_list)
###uncomment below function everytime you need to generate new activityGen related files 

# generateGraph(traci,edge_list,network)

