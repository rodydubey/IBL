from lxml import etree as ET
from sumolib import checkBinary
import os
import sys
import numpy as np
import traci
import csv

segmentLength = 25
def loopDetector(traci,edge_list,filename):
    
    dataList = []
    for edge_id in edge_list:
        lane_count = traci.edge.getLaneNumber(edge_id)
        lane_index = 0
        # if edge_id == "-840":
        while lane_index < lane_count:
            lane_id = edge_id + "_" + str(lane_index)
            length = traci.lane.getLength(lane_id)

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
            lane_index+=1

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
    writeAdditionalFilesForLoopDetector()

def writeAdditionalFilesForLoopDetector():
   
    data = ET.Element('additionals')
    with open('../sumo_config/loopDetectorList.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            s_elem1 = ET.SubElement(data, 'e1Detector')
            s_elem1.set('id', row[1])
            s_elem1.set('lane', row[0])
            s_elem1.set('pos', row[2])
            s_elem1.set('freq', '10000')
            s_elem1.set('file', 'loopDetectors.out.xml')


    b_xml = ET.tostring(data, pretty_print=True)
 
    # Opening a file under the name `items2.xml`,
    # with operation mode `wb` (write + binary)
    with open("../sumo_config/loopDetectors_temp.add.xml", "wb") as f:
        f.write(b_xml)


            





