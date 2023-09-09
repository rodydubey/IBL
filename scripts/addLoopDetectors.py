from lxml import etree as ET
from sumolib import checkBinary
import os
import sys
import numpy as np
import traci
import csv

segmentLength = 25
def loopDetector(network,edge_list,filename):
    
    dataList = []
    for edge_id in edge_list:
        lanes = network.getEdge(edge_id).getLanes()

        # lane_index = 0
        # if edge_id == "-840":
        for lane in lanes:
            # lane_id = edge_id + "_" + str(lane_index)
            # length = traci.lane.getLength(lane_id)
            length = lane.getLength()
            lane_id = lane.getID()
            # # divide the lane into N segements of 25 meters
            # numberOfSegment = int(length/segmentLength)
            # loopCounter = 0
            # pos = 0
            # while loopCounter < numberOfSegment:
            #     loopDetectorId = "det_" + lane_id + "_" + str(loopCounter)
            #     pos = 12.5 + 25*loopCounter              
            #     print(lane_id,loopDetectorId,"---",pos)
            #     data = [lane_id,loopDetectorId,pos]
            #     dataList.append(data)
            #     loopCounter+=1

            # for scenario when two loop detectors are needed. One at the begining and another at the end.
            loopDetectorId = "det_" + lane_id + "_" + str(0)
            pos = 0
            data = [lane_id,loopDetectorId,pos]
            dataList.append(data)
            loopDetectorId = "det_" + lane_id + "_" + str(1)
            pos = length
            data = [lane_id,loopDetectorId,pos]
            dataList.append(data)

            
            # print(numberOfSegment)
            # lane_index+=1

    # write dataList to a CSV file
    # header = ['Lane_ID','Loop Detector Id', 'Loop Detector Position']
    with open('../sumo_config/loopDetectorList.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        # writer.writerow(header)
        # write multiple rows
        writer.writerows(dataList)
                # print(length)

    # write additional file for sumocfg
    writeAdditionalFilesForLoopDetector(edge_list)

def writeAdditionalFilesForLoopDetector(edge_list):
   
    data = ET.Element('additionals')
    with open('../sumo_config/loopDetectorList.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            s_elem1 = ET.SubElement(data, 'e1Detector')
            s_elem1.set('id', row[1])
            s_elem1.set('lane', row[0])
            s_elem1.set('pos', row[2])
            s_elem1.set('freq', '300')
            s_elem1.set('file', 'loopDetectors.out.xml')

    edata_bus = ET.SubElement(data, 'edgeData')
    edata_bus.set('id', 'edgestats_bus')
    edata_bus.set('freq', '300')
    edata_bus.set('file', 'edgestats.out.xml')

    edata_cars = ET.SubElement(data, 'edgeData')
    edata_cars.set('id', 'edgestats_cars')
    edata_cars.set('freq', '300')
    edata_cars.set('file', 'edgestats.out.xml')

    b_xml = ET.tostring(data, pretty_print=True)
 
    # Opening a file under the name `items2.xml`,
    # with operation mode `wb` (write + binary)
    with open("../sumo_config/loopDetectors.add.xml", "wb") as f:
        f.write(b_xml)


            





