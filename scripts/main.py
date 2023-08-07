from sumolib import checkBinary
import traci
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

withGUI = True

if not withGUI:
    try:
        import libsumo as traci
    except:
        pass
# sumo things - we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoCMD = ["--time-to-teleport.disconnected",str(1),"--ignore-route-errors","--device.rerouting.probability","1","--device.rerouting.period","1",
                "--pedestrian.striping.dawdling","0.5","--collision.check-junctions", str(True),"--collision.mingap-factor","0","--collision.action", "warn",
                    "--seed", "42", "-W","--default.carfollowmodel", "IDM","--no-step-log","--statistic-output","output.xml"]
if withGUI:
    sumoBinary = checkBinary('sumo-gui')
    sumoCMD += ["--start", "--quit-on-end"]
else:
    sumoBinary = checkBinary('sumo')

print(sumoBinary)
sumoConfig = "../sumo_config/SimpleRandom.sumocfg"
sumoCMD = ["-c", sumoConfig] + sumoCMD

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



###uncomment below function everytime you need to generate new activityGen related files 
writeActivityGenSupportingData(networkFileName,edge_list)
###uncomment below function everytime you need to generate new activityGen related files 

###uncomment below function everytime you need to generate new Loop  detector additional file
# loopDetector(traci,edge_list,loopDetectorFileName)
###uncomment below function everytime you need to generate new Loop  detector additional file

# generateGraph(traci,edge_list,network)

getEdgesBetweenOD(network)
# while step < 100:
#     traci.simulationStep()
#     # nLanes = traci.lane.getIDList()
#     # nEdges = traci.edge.getIDList()

#     # for edge_id in nEdges:   
#     # if edge_id.find("_") == -1: # filters edges from internal edges
#     #         edge_list.append(edge_id)

#     # for edge_id in edge_list:
#     #     lane_id = edge_id + "_0"
#     #     length = traci.lane.getLength(lane_id)
#     #     print(lane_id,"--",length)
#     step += 1

# traci.close()

