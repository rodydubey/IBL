from sumolib import checkBinary
import numpy as np
import os, sys
from sumolib import net
from random import randrange
import json
import math
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


# sumoCMD = ["--time-to-teleport.disconnected",str(10),"--seed", "42", "-W","--default.carfollowmodel", "IDM","--no-step-log","--statistic-output","output.xml" #"--begin","22000"
#                     ]

sumoCMD = ["--time-to-teleport.disconnected",str(40),"--ignore-route-errors",
						"--collision.check-junctions", str(True),"--collision.mingap-factor","0","--collision.action", "warn",
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
routesJsonFileName = '../sumo_config/Routes.json'

traci.start([sumoBinary] + sumoCMD)
daySeconds = 86400
stepCounter = 0
edge_list = [] # list of all edges
candidate_bus_lanes = [] # list of all lanes that can be adapted to bus lanes
network = net.readNet(networkFileName)
nEdges = [e.getID() for e in network.getEdges()]


ListOfStreetLength = []
for edge_id in nEdges:   
    if edge_id.find("_") == -1: # filters edges from internal edges
        edge_list.append(edge_id)
        edgeLength = network.getEdge(edge_id).getLength()
        ListOfStreetLength.append(edgeLength)
        # print(edgeLength)
# print(edge_list)

#compute Standard Distance and Mean of all edge length (i.e., distance between loop detectors)
std_dev = np.std(ListOfStreetLength)
mean = np.mean(ListOfStreetLength)
# print(std_dev)
for edge_id in edge_list:
    lanes = network.getEdge(edge_id).getLanes()
    for lane in lanes:
        lane_id = lane.getID()
        if "_0" in lane_id:
            candidate_bus_lanes.append(lane_id)
# print(math.exp(-math.sqrt(4*100/mean)))
#Write weighted Adjacency matrix
with open('../dataset/adj.csv','w') as adj_file:
    for edge_id in edge_list:
        text=''
        for edge_id2 in edge_list:
                #check if edge_id is connected to edge_id2. If yes compute degree/edge length
            # if edge_id == edge_id2:
            #     text = text + str(1) + ','
            # else:
            nextEdges = network.getEdge(edge_id).getOutgoing()
            listOfEdges = [li.getID() for li in nextEdges]
            degree = len(listOfEdges)
            edgeLength = network.getEdge(edge_id).getLength()
            flag = False
            for nex in listOfEdges:
                if edge_id2 in nex:
                    flag = True                
            if flag:
                weight = math.exp(-np.sqrt(degree*edgeLength/np.square(mean)))
                text = text + str(weight) + ','
            else:
                text = text + str(0) + ','
        # print(text)
        adj_file.write(text)
        adj_file.write('\n')  
adj_file.close()
  
all_traffic = ['pedestrian','private', 'emergency', 'passenger','authority', 'army', 'vip', 'hov', 'taxi', 'bus', 'coach', 'delivery', 'truck', 'trailer', 'motorcycle', 'moped', 'evehicle', 'tram', 'rail_urban', 'rail', 'rail_electric', 'rail_fast', 'ship', 'custom1', 'custom2']

f = open(routesJsonFileName)
routeData = json.load(f)
timeOftheDay = 0
TwoDFeatureArray = np.zeros((len(candidate_bus_lanes),5))
NodeFeatureArray = np.zeros((params.timeSlotForDayDivider,len(candidate_bus_lanes),5))
print(NodeFeatureArray.shape)

# with open('../dataset/NodeFeatures.csv','w') as file:
while stepCounter < daySeconds:
    traci.simulationStep(stepCounter)   
    ######### INSERT CODE FOR MODIFYING PERMISSIONS HERE ########
    if stepCounter % params.detectorMeasurementInterval == 0:
        timeOftheDay+=1
        isIntermittent = False
        IBL_lanes = [] # temp IBL lanes
        lineList = []
        print(str(stepCounter) + "---" + str(traci.inductionloop.getLastIntervalVehicleNumber("det_-15_2_1_passenger")))
        nodeIndex = 0
        for candidate_lane in candidate_bus_lanes:            
            lane_qualifier = randrange(3) # 0 = all, 1 = dedicated bus lane, 2 = IBL
            # lane_qualifier = 2
            
            lane_length = traci.lane.getLength(candidate_lane)
            lane_speed = traci.lane.getMaxSpeed(candidate_lane)
                            
            strippedLaneIndex = candidate_lane.split('_')[0]
            #NODE FEATURES - edge belongs to a bus route, number of bus stops at this edge, lane mode, lane length, lane speed
            # listOfBusOnAllLanes = []
            
            bus_count_lane_0 = "det_" + strippedLaneIndex + "_0_1_bus"
            bus_count_lane_1 = "det_" + strippedLaneIndex + "_1_1_bus"
            bus_count_lane_2 = "det_" + strippedLaneIndex + "_2_1_bus"

            passenger_count_lane_0 = "det_" + strippedLaneIndex + "_0_1_passenger"
            passenger_count_lane_1 = "det_" + strippedLaneIndex + "_1_1_passenger"
            passenger_count_lane_2 = "det_" + strippedLaneIndex + "_2_1_passenger"

            CountOfBusOnAllLanes = traci.inductionloop.getLastIntervalVehicleNumber(bus_count_lane_0) 
            + traci.inductionloop.getLastIntervalVehicleNumber(bus_count_lane_1)
            + traci.inductionloop.getLastIntervalVehicleNumber(bus_count_lane_2)

            CountOfPassengersOnAllLanes = traci.inductionloop.getLastIntervalVehicleNumber(passenger_count_lane_0) 
            + traci.inductionloop.getLastIntervalVehicleNumber(passenger_count_lane_1)
            + traci.inductionloop.getLastIntervalVehicleNumber(passenger_count_lane_2)               

            # text = str(stepCounter) + "_" + str(strippedLaneIndex) + "_" + str(CountOfBusOnAllLanes) + "_" + str(CountOfPassengersOnAllLanes) + "_" + str(lane_qualifier)
            # lineList.append(text)
            feature_array = np.array([timeOftheDay/params.timeSlotForDayDivider,CountOfBusOnAllLanes,CountOfPassengersOnAllLanes,lane_qualifier,params.dayOfTheWeek])
            TwoDFeatureArray[nodeIndex] = feature_array
            nodeIndex+=1
            # print(text)          
            tempLaneIndex1 = strippedLaneIndex + '_1'
            tempLaneIndex2 = strippedLaneIndex + '_2'
            if lane_qualifier == 0:
                traci.lane.setAllowed(candidate_lane,all_traffic)
                # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                traci.lane.setAllowed(tempLaneIndex2,all_traffic)
            elif lane_qualifier == 1:
                traci.lane.setDisallowed(candidate_lane,all_traffic)
                traci.lane.setAllowed(candidate_lane,'bus')
                # traci.lane.setDisallowed(tempLaneIndex1,'bus')
                traci.lane.setDisallowed(tempLaneIndex2,'bus')
            else:
                IBL_lanes.append(candidate_lane)
        # for line in lineList:
        #     file.write(line + ",")
        # file.write('\n')
        NodeFeatureArray[timeOftheDay-1][:][:] = TwoDFeatureArray
        # print(NodeFeatureArray)
    #### USE A FLAG FOR INTERMITTENT ####
    # isIntermittent = True
    if stepCounter % params.intermittentPeriods == 0:
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
                # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                traci.lane.setAllowed(tempLaneIndex2,all_traffic)
                # traci.lane.setDisallowed(tempLaneIndex1,'bus')
                traci.lane.setDisallowed(tempLaneIndex2,'bus')                    
            else:
                # print("Only Bus")                               
                traci.lane.setAllowed(IBL_lane,all_traffic)
                # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                traci.lane.setAllowed(tempLaneIndex2,all_traffic)            
    stepCounter +=1 
# file.close()      
traci.close()

#convert node and edge data from csv to .npy format
adj_data = np.genfromtxt('..\\dataset\\adj.csv', delimiter=',')
np.save('..\\dataset\\adj.npy', adj_data)
np.save('..\\dataset\\nodeFeatures.npy',NodeFeatureArray)
#timestamp per day = 24*4 (96)if the data is recorded every 15 mins
# 96*numberOfNodes*NumberOfFeatures Features( time,number of cars, number of buses, lane_type,weekday) time = counterID/96, weekday = weekday/7
# 288*280*8

