from lxml import etree as ET
from sumolib import checkBinary
import os
import sys
import numpy as np
import traci
import csv
import random
import json
 
def writeActivityGenSupportingData(traci,edge_list):
   
    #Write streets info 
    # <streets>
		# <street edge="e01t11" population="10" workPosition="100" />
    # </streets>
    xmlfile = "../sumo_config/activitygen_base.stat.xml"
    stattree = ET.parse(xmlfile)
    city = stattree.getroot()
    streets = city.find('streets')
    city.remove(streets)

    data = ET.Element('streets')
    busStations_data = ET.Element('busStations')
    busStops_data = ET.Element('busStops')
    bus_station_counter = 1
    busStationToEdgeDict = {}
    for edge_id in edge_list:
        s_elem1 = ET.SubElement(data, 'street')
        s_elem1.set('edge', edge_id)
        population = random.randrange(100)
        s_elem1.set('population', str(population))
        s_elem1.set('workPosition', str(100 - population))

        #Write <cityGates> info 
        #<cityGates>
            #<entrance edge="-840" pos="1" incoming="0.05" outgoing="0.05" />
        #</cityGates> --- TO DO
        numberOfCityGates = 20 # can be any number based on the network size

        #Write BusStations info 
        #<busStations>
            #<busStation id="1" edge="e11t12" pos="10" />
        #</busStations>
        lane_id = edge_id + "_0"
        edge_length = traci.lane.getLength(lane_id)        
        s_elem2 = ET.SubElement(busStations_data, 'busStation')
        s_elem2.set('id', str(bus_station_counter))
        s_elem2.set('edge', edge_id)
        busStationToEdgeDict[edge_id] = bus_station_counter
        #random position on an edge
        pos = random.randrange(int(edge_length-10))
        s_elem2.set('pos', str(pos))

        #Write additionalFile for sumocfg regarding busstop location and visualization
        #<busStop id="bs_0" lane="-840_0" startPos="143.78" endPos="153.78" lines="101"/>   

        s_elem3 = ET.SubElement(busStops_data, 'busStop')
        s_elem3.set('id', str(bus_station_counter))
        s_elem3.set('lane', lane_id)
        s_elem3.set('startPos', str(pos))
        s_elem3.set('endPos', str(pos+10))
        s_elem3.set('lines', "101 102 103 104 105 106 107")
        bus_station_counter+=1

    #write busLines
    # <busLines>
    #     <busLine id="101" maxTripDuration="10">
    #         <stations>
    #             <station refId="1" />
    #         </stations>
    #         <revStations>
    #             <station refId="109" />
    #         </revStations>
    #         <frequencies>
    #             <frequency begin="21600" end="36000" rate="300" />
    #         </frequencies>
    #     </busLine>
    # </busLines>
    #NOTE: Routes.json file should be pre-written for this part to work

    
    # Opening JSON file
    f = open('../sumo_config/Routes.json')
    
    # returns JSON object as
    # a dictionary
    data_route = json.load(f)
    
    # Iterating through the json
    # list
    buslineID = 101          
    data_busLines = ET.Element('busLines')
    
    for route in data_route:
        # print(route)
        # print(buslineID)
        s_elem4 = ET.SubElement(data_busLines, 'busLine')
        s_elem4.set('id', str(buslineID))
        s_elem4.set('maxTripDuration', '10')
        s_elem5 = ET.SubElement(s_elem4, 'stations')
        for r in route:
            busStopFromEdge = busStationToEdgeDict[r]     
            s_elem6 = ET.SubElement(s_elem5, 'station')
            s_elem6.set('refId', str(busStopFromEdge))
        
        reverseList = route[::-1]
        s_elem7 = ET.SubElement(s_elem4, 'revStations')
        for r_reverse in reverseList:
            r_reverse = int(r_reverse)
            if r_reverse < 0:      
                busStopFromEdge = busStationToEdgeDict[str(abs(r_reverse))]
            else:
                busStopFromEdge = busStationToEdgeDict[str(-r_reverse)]
            
            
            s_elem8 = ET.SubElement(s_elem7, 'station')
            s_elem8.set('refId', str(busStopFromEdge))

        s_elem9 = ET.SubElement(s_elem4, 'frequencies')
        i = 0
        while i <4:
            s_elem10 = ET.SubElement(s_elem9, 'frequency')
            s_elem10.set('begin', '21600')
            s_elem10.set('end', '36000')
            s_elem10.set('rate', '300')
            i+=1
        buslineID+=1
    
    #Read trip files and create bus route type with busStops. NOTE: file test_trips.rou.xml should be created first
    # <vehicle id ="bl101b1:1" type="BUS" depart="200" color="1,0,0">
    #     <route edges="-840 -642 -592 -332"/>
    #     <stop busStop="132" duration="30"/>
    #     <stop busStop="118" duration="30"/>
    #     <stop busStop="105" duration="30"/>
    #     <stop busStop="76" duration="30"/>
    # </vehicle>
    data_vType = ET.Element('vType')
    tree = ET.parse('../sumo_config/test_trips.rou.xml')
    root = tree.getroot()
    for trip in root.iter('trip'):
        if trip.attrib['type'] == "bus":            
            s_elem11 = ET.SubElement(data_vType, 'vehicle')
            s_elem11.set('id', trip.attrib['id'])
            s_elem11.set('type', "BUS")
            s_elem11.set('depart', trip.attrib['depart'])
            s_elem11.set('color', "0,0,1")

            # print(trip.attrib['id'],"---", trip.attrib['depart'])

            s_elem12 = ET.SubElement(s_elem11, 'route')
            edges = trip.attrib['from'] + " " + trip.attrib['via'] + " " + trip.attrib['to']
            # print(edges)
            s_elem12.set('edges', edges)
            edgeList = edges.split()
            for e in edgeList:
                # print(e)                
                s_elem13 = ET.SubElement(s_elem11, 'stop')
                busStopNumber = busStationToEdgeDict[str(e)]
                # print(busStopNumber)
                s_elem13.set('busStop', str(busStopNumber))
                s_elem13.set('duration', "30")



            


    # b_xml = ET.tostring(data,pretty_print=True)
    # c_xml = ET.tostring(busStations_data,pretty_print=True)
    # d_xml = ET.tostring(busStops_data,pretty_print=True)

    b_xml = ET.tostring(data, pretty_print=True)
    c_xml = ET.tostring(busStations_data, pretty_print=True)
    d_xml = ET.tostring(busStops_data, pretty_print=True)
    e_xml = ET.tostring(data_busLines, pretty_print=True)
    f_xml = ET.tostring(data_vType, pretty_print=True)
 
    # Opening a file under the name `items2.xml`,
    # with operation mode `wb` (write + binary)
    with open("../sumo_config/activitygenSupport.xml", "wb") as f:
        f.write(b_xml)
        f.write(c_xml)
        f.write(d_xml)
        f.write(e_xml)
        f.write(f_xml)

    # add what needs to be added to generate a new stat file
    city.append(data)
    city.append(busStations_data)
    city.append(data_busLines)
    ET.indent(stattree, space="  ")
    stattree.write("../sumo_config/act.stat.xml", pretty_print=True)