from sumolib import checkBinary
import numpy as np
import os, sys
from sumolib import net
from random import randrange
# sumo things - we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import params
import traci

"""
Configure various parameters of SUMO
"""

withGUI = True

if not withGUI:
    try:
        import libsumo as traci
    except:
        pass


sumoCMD = ["--time-to-teleport.disconnected",str(1),"--ignore-route-errors","--device.rerouting.probability","1","--device.rerouting.period","1",
                "--pedestrian.striping.dawdling","0.5","--collision.check-junctions", str(True),"--collision.mingap-factor","0","--collision.action", "warn",
                    "--seed", "42", "-W","--default.carfollowmodel", "IDM","--no-step-log","--statistic-output","output.xml","--begin","22000"
                    ]
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

traci.start([sumoBinary] + sumoCMD)
daySeconds = 86400
stepCounter = 0
edge_list = [] # list of all edges
candidate_bus_lanes = [] # list of all lanes that can be adapted to bus lanes
network = net.readNet(networkFileName)
nEdges = [e.getID() for e in network.getEdges()]

for edge_id in nEdges:   
    if edge_id.find("_") == -1: # filters edges from internal edges
        edge_list.append(edge_id)
# print(edge_list)

for edge_id in edge_list:
    lanes = network.getEdge(edge_id).getLanes()
    
    for lane in lanes:
        lane_id = lane.getID()
        if "_0" in lane_id:
            candidate_bus_lanes.append(lane_id)

# candidate_bus_lanes.append("325_0")
all_traffic = ['pedestrian','private', 'emergency', 'passenger','authority', 'army', 'vip', 'hov', 'taxi', 'bus', 'coach', 'delivery', 'truck', 'trailer', 'motorcycle', 'moped', 'evehicle', 'tram', 'rail_urban', 'rail', 'rail_electric', 'rail_fast', 'ship', 'custom1', 'custom2']
    
while stepCounter < daySeconds:

    ######### INSERT CODE FOR MODIFYING PERMISSIONS HERE ########
    # change lane perimission every 30 minutes
    if stepCounter % 1800 == 0:
        isIntermittent = False
        IBL_lanes = [] # temp IBL lanes
        for candidate_lane in candidate_bus_lanes:            
            lane_qualifier = randrange(2) # 0 = all, 1 = dedicated bus lane, 2 = IBL
            # lane_qualifier = 2
            strippedLaneIndex = candidate_lane.split('_')[0]
            tempLaneIndex1 = strippedLaneIndex + '_1'
            tempLaneIndex2 = strippedLaneIndex + '_2'
            if lane_qualifier == 0:
                traci.lane.setAllowed(candidate_lane,all_traffic)
                traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                traci.lane.setAllowed(tempLaneIndex2,all_traffic)
            elif lane_qualifier == 1:
                traci.lane.setDisallowed(candidate_lane,all_traffic)
                traci.lane.setAllowed(candidate_lane,'bus')
                traci.lane.setDisallowed(tempLaneIndex1,'bus')
                traci.lane.setDisallowed(tempLaneIndex2,'bus')
            else:
                isIntermittent = True
                IBL_lanes.append(candidate_lane)


    #### USE A FLAG FOR INTERMITTENT ####
    # isIntermittent = True
    intermittentPeriods = 6
    if isIntermittent:
        time_increment = params.measurementPeriod # 5 mins
    else:
        time_increment = params.measurementPeriod*intermittentPeriods # 30 mins

    if isIntermittent:
        for i in range(intermittentPeriods):
            stepCounter += time_increment
            traci.simulationStep(stepCounter)
            # intermittentPermissionToggleFunction()
            for IBL_lane in IBL_lanes:     
                strippedLaneIndex = IBL_lane.split('_')[0]
                tempLaneIndex1 = strippedLaneIndex + '_1'
                tempLaneIndex2 = strippedLaneIndex + '_2'            
                if 'bus' in traci.lane.getAllowed(IBL_lane) and 'passenger' in traci.lane.getAllowed(IBL_lane):
                    # print(traci.lane.getAllowed(IBL_lane))
                    # print("All traffic")
                    traci.lane.setDisallowed(IBL_lane,all_traffic)
                    traci.lane.setAllowed(IBL_lane,'bus')                      
                    traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                    traci.lane.setAllowed(tempLaneIndex2,all_traffic)
                    traci.lane.setDisallowed(tempLaneIndex1,'bus')
                    traci.lane.setDisallowed(tempLaneIndex2,'bus')
                    
                else:
                    # print("Only Bus")                               
                    traci.lane.setAllowed(IBL_lane,all_traffic)
                    traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                    traci.lane.setAllowed(tempLaneIndex2,all_traffic)
    else:
        stepCounter += time_increment
        traci.simulationStep(stepCounter)

traci.close()

