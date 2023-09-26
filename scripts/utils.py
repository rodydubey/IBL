import os, sys
import re
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
import pandas as pd
import igraph as ig
import numpy as np
import subprocess
import sumolib
import json

def reorder_df(df, fromto):
    cols = list(df)
    for _movecol in fromto[::-1]:
        cols.insert(0, cols.pop(cols.index(_movecol)))
    df = df.loc[:, cols]
    return df


def network2graph(netfile, ret_node=True, ret_edges=True):
    netfile = os.path.abspath(netfile)
    dirname = os.path.dirname(netfile)
    subprocess.run(f'netconvert -s {netfile} --plain-output-prefix plain', shell=True)
    subprocess.run(f'$SUMO_HOME/tools/xml/xml2csv.py plain.edg.xml', shell=True)
    subprocess.run(f'$SUMO_HOME/tools/xml/xml2csv.py plain.nod.xml', shell=True)
    nodes = pd.read_csv(f'plain.nod.csv', delimiter=';')
    edges = pd.read_csv(f'plain.edg.csv', delimiter=';')

    edges = reorder_df(edges, ['edge_from', 'edge_to'])
    nodes = reorder_df(nodes, ['node_id'])

    g = ig.Graph.DataFrame(edges, directed=True,
                           use_vids=False, vertices=nodes)
    mapping = {node_id: igraph_id for igraph_id, node_id in enumerate(g.vs['name'])}

    subprocess.run(f'rm plain*.xml plain*.csv', shell=True)
    _return = (g, mapping,)
    if ret_node: _return += (nodes,)
    if ret_edges: _return += (edges,)
    return _return


def get_paths(g, source, sink, mapping, k=1, mode='direct', output_sumo=True):
    '''
    if `mode` is "direct" find the k shortest paths based solely on weights.
    if `mode` is "indirect" we try to find k shortest paths with minimal overlap (alternate routes).
    '''
    if mode!='direct':
        paths = g.get_k_shortest_paths(mapping[source], to=mapping[sink], k=100, weights=None, mode='out', output='epath')[-1]

    else:
        paths = []
        factor = 2
        g.es['weight'] = 1

        for i in range(k):
            p = g.get_shortest_paths(mapping[source], to=mapping[sink], weights='weight', mode='out', output='epath')
            new_weights = np.array(g.es[p[0]]['weight'])*factor
            g.es[p[0]]['weight'] = new_weights
            paths.append(p[0])

    if output_sumo:
        paths = [g.es[p]['edge_id'] for p in paths]

    return paths


def parse_sumo_output(outfile='scenarios/random_grid/travel.out.xml'):
    travel_times = []
    delays = []
    tripinfos = sumolib.output.parse_sax__asList(outfile, "tripinfo", ['duration', 'timeLoss'])
    for trip in tripinfos:
        travel_times.append(trip['duration'])
        delays.append(trip['timeLoss'])
    return {"travel_times": travel_times,
            "delays": delays}

def parse_disaggregate_sumo_output(outfile='scenarios/random_grid/travel.out.xml'):
    travel_times = []
    delays = []
    route_ids = []
    car_ids = []
    tripinfos = sumolib.output.parse_sax__asList(outfile, "tripinfo", ['id','duration', 'timeLoss'])
    for trip in tripinfos:
        route_id, car_id = re.findall('\d+', trip['id'])
        route_ids.append(route_id)
        car_ids.append(car_id)
        travel_times.append(trip['duration'])
        delays.append(trip['timeLoss'])
    return {"travel_times": travel_times,
            "delays": delays}


def getEdgesBetweenOD(network):
    fromEdgeArray = [-840,-1797,-1404,-1891,-621,-1882,-1201]
    ToEdgeArray = [496,867,1483,1404,1464,601,686]
    itr = 101
    routes = {}
    for i, (source, target) in enumerate(zip(fromEdgeArray, ToEdgeArray)):
        routeID = str(itr)
        fromEdge = network.getEdge(str(source))
        toEdge = network.getEdge(str(target))
        path, cost = network.getOptimalPath(fromEdge,toEdge)
        for j, edges in enumerate([path, path[::-1]]): # build forward and reverse routes            
            revfactor = 1
            if j==1: # reverse route
                routeID += '_r'
                revfactor = -1
            edgeList = [revfactor*int(edge.getID()) for edge in edges]
            routes[routeID] = edgeList
        itr += 1
    json_string = json.dumps(routes)
    with open('../sumo_config/Routes.json', 'w') as outfile:
        outfile.write(json_string)

        
if __name__=="__main__":
    s = parse_sumo_output('../scenarios/random_grid/travel.out.xml')
    print(s)