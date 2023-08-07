import os
import sys
import numpy as np
import traci
import csv
from sumolib import net

def generateGraph(traci,edge_list,network):
    graphNodeList = []
    graphEdgeList = []
    for edge_id in edge_list:
        lane_count = traci.edge.getLaneNumber(edge_id)
        lane_index = 0
        while lane_index < lane_count:
            lane_id = edge_id + "_" + str(lane_index)
            length = traci.lane.getLength(lane_id)
            laneID = network.getLane(lane_id)

            #Node Related Calls
            detector_1_pos, detector_2_pos = traci.lane.getShape(lane_id)
            node_1 = "det_" + lane_id + "_" + str(0)
            node_2 = "det_" + lane_id + "_" + str(1)
            node_1_pos = traci.inductionloop.getPosition(node_1)
            node_2_pos = traci.inductionloop.getPosition(node_2)
            data = [node_1,detector_1_pos[0],detector_1_pos[1],node_1_pos]
            graphNodeList.append(data)
            data = [node_2,detector_2_pos[0],detector_2_pos[1],node_2_pos]
            graphNodeList.append(data)

            #Edge Related Calls
            data = [node_2,node_1,length]
            graphEdgeList.append(data)
            
            allIncomingConnection = laneID.getIncoming()
            for lane in allIncomingConnection:
                node_1_1 = "det_" + lane.getID() + "_" + str(1)
                node_1_1_pos,dontUse = traci.lane.getShape(lane.getID())
                length = traci.simulation.getDistance2D(detector_2_pos[0],detector_2_pos[1],node_1_1_pos[0],node_1_1_pos[1])
                data = [node_1_1,node_2,length]
                graphEdgeList.append(data)
            allOutgoingConnection = laneID.getOutgoingLanes()
            for lane in allOutgoingConnection:
                node_2_2 = "det_" + lane.getID() + "_" + str(0)
                dontUse,node_2_2_pos = traci.lane.getShape(lane.getID())
                length = traci.simulation.getDistance2D(detector_1_pos[0],detector_1_pos[1],node_2_2_pos[0],node_2_2_pos[1])
                data = [node_1,node_2_2,length]
                graphEdgeList.append(data)


            lane_index+=1

    with open('../sumo_config/GraphNodeList.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        # writer.writerow(header)
        # write multiple rows
        writer.writerows(graphNodeList)

    with open('../sumo_config/GraphEdgeList.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        # writer.writerow(header)
        # write multiple rows
        writer.writerows(graphEdgeList)

        # edgeID = network.getEdge('-840')
        # laneID = network.getLane('-642_1')
        # # print(laneID.getID())
        # allIncomingConnection = laneID.getIncoming()
        # allOutgoingConnection = laneID.getOutgoingLanes()

        # for lane in allIncomingConnection:
        #     print(lane.getID())
        
        # for lanee in allOutgoingConnection:
        #     print(lanee.getID())
    # fromNode = edgeID.getFromNode()
    # toNode = edgeID.getToNode()
    # incoming = toNode.getIncoming()
    # nodeList = net.getNodes()
    # print(fromNode.getID(),"---",toNode.getID())
    # for node in nodeList:
    #     print(node)
    #     node