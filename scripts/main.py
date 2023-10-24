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

network = net.readNet(networkFileName)

edge_list = [e.getID() for e in network.getEdges(withInternal=False)] # list of all edges excluding internal links

# Write additional file with loop detectors if the file does not exist

###uncomment below function everytime you need to generate new Loop  detector additional file
loopDetector(network, edge_list, loopDetectorFileName)
###uncomment below function everytime you need to generate new Loop  detector additional file

getEdgesBetweenOD(network)

###uncomment below function everytime you need to generate new activityGen related files 
writeActivityGenSupportingData(networkFileName,edge_list)
###uncomment below function everytime you need to generate new activityGen related files 

# generateGraph(traci,edge_list,network)

