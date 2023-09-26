from lxml import etree as ET
from sumolib import checkBinary
import sumolib
import os
import sys
import numpy as np
import traci
import csv
import random
import json
import re
import subprocess
import matplotlib.colors as cm
import matplotlib.pyplot as plt


colors = [cm.to_rgb(plt.cm.tab20(i)) for i in range(20)]

def writeActivityGenSupportingData(netFileName, edge_list):
   
    #Write streets info 
    # <streets>
		# <street edge="e01t11" population="10" workPosition="100" />
    # </streets>
    network = sumolib.net.readNet(netFileName)

    xmlfile = "../sumo_config/activitygen_base.stat.xml"
    stattree = ET.parse(xmlfile)
    city = stattree.getroot()
    # streets = city.find('streets')
    # city.remove(streets)

    # Opening JSON file
    with open('../sumo_config/Routes.json') as f:
        # returns JSON object as a dictionary
        buslinedict = json.load(f)

    bus_route_edges = set([item for sublist in buslinedict.values() for item in sublist])
    bus_route_edges.update(set([str(-int(i)) for i in bus_route_edges])) # Assume all reverse edges are also part of bus_routes

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
        if edge_id in bus_route_edges:

            lane_id = edge_id + "_0"
            lane = network.getLane(lane_id)
            edge_length = lane.getLength()        
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

    # Iterating through the json
    # list
    # buslineID = 101          
    data_busLines = ET.Element('busLines')
    # build route file from busStations and busLines
    routesxml = ET.Element('routes')
    # buslinedict = {}
    for i, (buslineID, route) in enumerate(buslinedict.items()):
        # build bus route xml
        route = [str(r) for r in route]
        routexml = ET.SubElement(routesxml, 'route')
        routeID = str(buslineID)
        routexml.set('id', routeID)
        route_str = ' '.join(route)
        routexml.set('color', ','.join(map(str,colors[i])))
        routexml.set('edges', route_str)
        buslinedict[routeID] = route_str
        for r in route[1:-1]:
            busStopFromEdge = busStationToEdgeDict[r]   

            stopsxml = ET.SubElement(routexml, 'stop')
            stopsxml.set('busStop', str(busStopFromEdge))
            stopsxml.set('duration', "30")

        if '_r' not in routeID:
            x_busline = ET.SubElement(data_busLines, 'busLine')
            x_busline.set('id', routeID)
            x_busline.set('maxTripDuration', '10')
            x_stations = ET.SubElement(x_busline, 'stations')
            for r in route:
                busStopFromEdge = busStationToEdgeDict[r]     
                x_station = ET.SubElement(x_stations, 'station')
                x_station.set('refId', str(busStopFromEdge))

            s_elem9 = ET.SubElement(x_busline, 'frequencies')
            periods = [(18000, 25200), (25200, 36000), (36000, 57600), (57600, 72000), (72000, 86399)] # 5, 7, 10, 16, 20, 23:59:59
            for i, (start, end) in enumerate(periods):
                s_elem10 = ET.SubElement(s_elem9, 'frequency')
                s_elem10.set('begin', str(start))
                s_elem10.set('end', str(end))
                s_elem10.set('rate', '300') # time between two buses in seconds
        else:
            assert routeID[:-2]==x_busline.attrib['id'] # same as previous
            # reverseList = route[::-1]
            x_revStation = ET.SubElement(x_busline, 'revStations')
            for r_reverse in route:
                busStopFromEdge = busStationToEdgeDict[r_reverse]
                x_station = ET.SubElement(x_revStation, 'station')
                x_station.set('refId', str(busStopFromEdge))
    

    # add what needs to be added to generate a new stat file
    city.append(data)
    city.append(busStations_data)
    city.append(data_busLines)
    ET.indent(stattree, space="  ")
    stattree.write("../sumo_config/act.stat.xml", pretty_print=True)

    subprocess.call(f'activitygen --net-file {netFileName} --stat-file ../sumo_config/act.stat.xml --output-file ../sumo_config/test.xml',
                     shell=True)


    #Read trip files and create bus route type with busStops. NOTE: file test_trips.rou.xml should be created first
    # <vehicle id ="bl101b1:1" type="BUS" depart="200" color="1,0,0">
    #     <route edges="-840 -642 -592 -332"/>
    #     <stop busStop="132" duration="30"/>
    #     <stop busStop="118" duration="30"/>
    #     <stop busStop="105" duration="30"/>
    #     <stop busStop="76" duration="30"/>
    # </vehicle>
    errctr = 0
    data_vType = ET.Element('vType')
    # tripstree = ET.parse('../sumo_config/test_trips.rou.xml')
    tripstree = ET.parse('../sumo_config/test.xml')
    tripsroot = tripstree.getroot()
    for vtype in tripsroot.iter('vType'):
        if vtype.attrib['vClass']=="bus":
            del vtype.attrib['color']
    for trip in tripsroot.iter('trip'):
        if trip.attrib['type'] == "bus":            
            s_elem11 = ET.SubElement(data_vType, 'vehicle')
            s_elem11.set('id', trip.attrib['id'])
            s_elem11.set('type', "bus")
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


            try:
                buslineID = re.search(r'bl(\d+)b*', trip.attrib['id']).group(1)
                if edges!=buslinedict[buslineID]: # this is a reverse route
                    buslineID += '_r'
                    assert edges == buslinedict[buslineID]
                trip.set('route', buslineID)
                del trip.attrib['from']
                del trip.attrib['via']
                del trip.attrib['to']
                trip.tag = 'vehicle'
            except:
                errctr+=1
                print(f'{trip.attrib["id"]} is not a bus. Removing item')
                trip.getparent().remove(trip)

    if errctr:
        print(f'{errctr} buses have route errors')

    additionalxml = ET.Element('additional')
    additionaltree = ET.ElementTree(additionalxml)
    for bs in busStops_data:
        additionalxml.append(bs)
    ET.indent(additionaltree, space="  ")
    additionaltree.write("../sumo_config/busStop.add.xml", pretty_print=True)

    for r in routesxml:
        tripsroot.insert(0,r)
    ET.indent(tripstree, space="  ")
    tripstree.write("../sumo_config/processed_trips.xml", pretty_print=True)