from sumolib import checkBinary
import numpy as np
import os, sys
from sumolib import net, xml
from random import randrange
import json
import math
import random
# sumo things - we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import params
import traci

import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-gui", action='store_true',
                        help="run without the SUMO gui")

    return parser.parse_args()


def forceChangeLane(bus_lane_id):
    #Start: Change Lane for all cars on IBL_Lane
    #find all vehicles on a bus lane
    allVehicles = traci.lane.getLastStepVehicleIDs(bus_lane_id)
    if len(allVehicles) > 1:
        for vehID in allVehicles:
            if vehID.find('bl') == -1: # not a bus
                traci.vehicle.changeLane(vehID, 1, params.laneChangeAttemptDuration)
    #End: Change Lane for all cars on IBL_Lane      


def generateData(seed,loopDetectorFileName,networkFileName,busStopsFileName,routesJsonFileName,withGUI):
    sumoCMD = ["--time-to-teleport.disconnected",str(40),"--ignore-route-errors",
                            "--collision.check-junctions", str(True),"--collision.mingap-factor","0","--collision.action", "warn",
                            "--seed", str(seed), "-W","--default.carfollowmodel", "IDM","--no-step-log","--statistic-output","output.xml"]
    # sumoCMD = ["--ignore-route-errors",
    #                         "--collision.check-junctions", str(True),"--collision.mingap-factor","0","--collision.action", "warn",
    #                         "--seed", "42","--default.carfollowmodel", "IDM","--statistic-output","output.xml"]

    if withGUI:
        sumoBinary = checkBinary('sumo-gui')
        sumoCMD += ["--start", "--quit-on-end"]
    else:
        sumoBinary = checkBinary('sumo')

    print(sumoBinary)
    sumoConfig = "../sumo_config/SimpleRandom.sumocfg"
    sumoCMD = ["-c", sumoConfig] + sumoCMD


    random.seed(seed)
    traci.start([sumoBinary] + sumoCMD)
    daySeconds = 86400 #86400
    stepCounter = 0
    candidate_bus_lanes = [] # list of all lanes that can be adapted to bus lanes
    network = net.readNet(networkFileName)
    edges = network.getEdges(withInternal=False)
    edge_list = [e.getID() for e in edges] # list of all edges excluding internal

    ListOfStreetLength = []
    for edge_id in edge_list:   
        edgeLength = network.getEdge(edge_id).getLength()
        ListOfStreetLength.append(edgeLength)

    #compute Standard Distance and Mean of all edge length (i.e., distance between loop detectors)
    std_dev = np.std(ListOfStreetLength)
    mean = np.mean(ListOfStreetLength)
    # print(std_dev)
    for busStop in xml.parse(busStopsFileName, 'busStop'):
        candidate_bus_lanes.append(busStop.lane)
 
    
    all_traffic = ['pedestrian','private', 'emergency', 'passenger','authority', 'army', 'vip', 'hov', 'taxi', 'bus', 'coach', 'delivery', 'truck', 'trailer', 'motorcycle', 'moped', 'evehicle', 'tram', 'rail_urban', 'rail', 'rail_electric', 'rail_fast', 'ship', 'custom1', 'custom2']

    timeOftheDay = 0
    TwoDFeatureArray = np.zeros((len(edges),5))
    NodeFeatureArray_Temp = np.zeros((params.timeSlotForDayDivider,len(edges),5))

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
            for nodeIndex, edge in enumerate(edges):            
                lane_qualifier = randrange(3) # 0 = all, 1 = dedicated bus lane, 2 = IBL
                # lane_qualifier = 2

                edge_id = edge.getID()
                lane_length = edge.getLength()
                lane_speed = edge.getSpeed()
                                
                #NODE FEATURES - edge belongs to a bus route, number of bus stops at this edge, lane mode, lane length, lane speed
                # listOfBusOnAllLanes = []
                
                CountOfBusOnAllLanes = 0
                CountOfPassengersOnAllLanes = 0
                for lane in edge.getLanes():
                    lane_id = lane.getID()
                    bus_detector = f'det_{lane_id}_1_bus'
                    car_detector = f'det_{lane_id}_1_passenger'

                    CountOfBusOnAllLanes = traci.inductionloop.getLastIntervalVehicleNumber(bus_detector) 
                    CountOfPassengersOnAllLanes = traci.inductionloop.getLastIntervalVehicleNumber(car_detector) 
            
                # text = str(stepCounter) + "_" + str(strippedLaneIndex) + "_" + str(CountOfBusOnAllLanes) + "_" + str(CountOfPassengersOnAllLanes) + "_" + str(lane_qualifier)
                # lineList.append(text)
                feature_array = np.array([timeOftheDay/params.timeSlotForDayDivider,CountOfBusOnAllLanes,CountOfPassengersOnAllLanes,lane_qualifier,params.dayOfTheWeek])
                TwoDFeatureArray[nodeIndex] = feature_array
                
                # print(text)          

                if f'{edge_id}_0' in candidate_bus_lanes: # only change permissions for candidate bus lanes
                    tempLaneIndex1 = f'{edge_id}_1'
                    tempLaneIndex2 = f'{edge_id}_2'
                    bus_lane_id = f'{edge_id}_0'
                    if lane_qualifier == 0:
                        traci.lane.setAllowed(bus_lane_id,all_traffic) # empty list means all vehicles are allowed.
                        # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                        traci.lane.setAllowed(tempLaneIndex2,all_traffic)
                    elif lane_qualifier == 1:
                        # traci.lane.setDisallowed(bus_lane_id,all_traffic) # redundant with setAllowed?
                        traci.lane.setAllowed(bus_lane_id,'bus')
                        # traci.lane.setDisallowed(tempLaneIndex1,'bus')
                        traci.lane.setDisallowed(tempLaneIndex2,'bus')
                        forceChangeLane(bus_lane_id)
                    else:
                        IBL_lanes.append(bus_lane_id)
            # for line in lineList:
            #     file.write(line + ",")
            # file.write('\n')
            NodeFeatureArray_Temp[timeOftheDay-1][:][:] = TwoDFeatureArray
            # print(NodeFeatureArray)
        #### USE A FLAG FOR INTERMITTENT ####
        # isIntermittent = True
        if stepCounter % params.intermittentPeriods == 0:
            # intermittentPermissionToggleFunction()
            for IBL_lane in IBL_lanes:     
                edge_id = IBL_lane.split('_')[0]
                tempLaneIndex1 = f'{edge_id}_1'
                tempLaneIndex2 = f'{edge_id}_2'
                allowed_vehicles = traci.lane.getAllowed(IBL_lane)
                if 'bus' in allowed_vehicles and 'passenger' in allowed_vehicles:
                    # print(traci.lane.getAllowed(IBL_lane))
                    # print("All traffic")
                    # traci.lane.setDisallowed(IBL_lane,all_traffic)
                    traci.lane.setAllowed(IBL_lane,'bus')   

                    forceChangeLane(IBL_lane)

                    # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                    traci.lane.setAllowed(tempLaneIndex2,all_traffic)
                    # traci.lane.setDisallowed(tempLaneIndex1,'bus')
                    # traci.lane.setDisallowed(tempLaneIndex2,'bus')                    
                else:
                    # print("Only Bus")                               
                    traci.lane.setAllowed(IBL_lane,all_traffic)
                    # traci.lane.setAllowed(tempLaneIndex1,all_traffic)
                    traci.lane.setAllowed(tempLaneIndex2,all_traffic)
        stepCounter += params.intermittentPeriods
    traci.close()
    # print(NodeFeatureArray_Temp)
    return NodeFeatureArray_Temp


    #timestamp per day = 24*4 (96)if the data is recorded every 15 mins
    # 96*numberOfNodes*NumberOfFeatures Features( time,number of cars, number of buses, lane_type,weekday) time = counterID/96, weekday = weekday/7
    # 288*280*8

if __name__ == "__main__":
    args = parse_args()

    """
    Configure various parameters of SUMO
    """
    withGUI = not args.no_gui

    if not withGUI:
        try:
            import libsumo as traci
        except:
            pass

    loopDetectorFileName = "../sumo_config/loopDetectors.add.xml"
    networkFileName = '../sumo_config/SimpleRandom.net.xml'
    busStopsFileName = '../sumo_config/busStop.add.xml'
    routesJsonFileName = '../sumo_config/Routes.json'

    ##WRITE ADJ MATRIX
    candidate_bus_lanes = [] # list of all lanes that can be adapted to bus lanes
    network = net.readNet(networkFileName)
    edges = network.getEdges(withInternal=False)
    edge_list = [e.getID() for e in edges] # list of all edges excluding internal

    ListOfStreetLength = []
    for edge_id in edge_list:   
        edgeLength = network.getEdge(edge_id).getLength()
        ListOfStreetLength.append(edgeLength)

    #compute Standard Distance and Mean of all edge length (i.e., distance between loop detectors)
    std_dev = np.std(ListOfStreetLength)
    mean = np.mean(ListOfStreetLength)
    # print(std_dev)
    for busStop in xml.parse(busStopsFileName, 'busStop'):
        candidate_bus_lanes.append(busStop.lane)
    # print(math.exp(-math.sqrt(4*100/mean)))
    #Write weighted Adjacency matrix
    with open('../dataset/adj_large.csv','w') as adj_file:
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
            text = text.rstrip(',')
            adj_file.write(text)
            adj_file.write('\n')  
    adj_file.close()

    adj_data = np.genfromtxt('../dataset/adj_large.csv', delimiter=',')
    # np.save('../dataset/adj_large.npy', adj_data)

    numberOfDays = 10
    NodeFeatureArray = np.zeros((params.timeSlotForDayDivider*numberOfDays,len(edges),5))
    print(NodeFeatureArray.shape)

    for i in range(numberOfDays): # Seeds 0 to 9 for weekdays. Seeds 10 to 20 for Weekends
        seed = i + 10
        print(seed,numberOfDays)
        outputArray = generateData(seed,loopDetectorFileName,networkFileName,busStopsFileName,routesJsonFileName,False)
        
        NodeFeatureArray = np.vstack((NodeFeatureArray, outputArray))
        # np.concatenate((NodeFeatureArray, outputArray))
        # print(NodeFeatureArray)
            
    #convert node and edge data from csv to .npy format   
    np.save('../dataset/node_values_Weekend_1To10.npy',NodeFeatureArray)   

