from sumolib import checkBinary
import numpy as np
import os, sys
# sumo things - we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
from addLoopDetectors import loopDetector
from generateGraph import generateGraph
from utils import getEdgesBetweenOD
import params
import traci

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

traci.start([sumoBinary] + sumoCMD)
daySeconds = 86400
stepCounter = 0
edge_list = [] # list of all edges

while stepCounter < daySeconds:

    ######### INSERT CODE FOR MODIFYING PERMISSIONS HERE ########

    #### USE A FLAG FOR INTERMITTENT ####
    isIntermittent = True
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
    else:
        stepCounter += time_increment
        traci.simulationstepCounter(stepCounter)

traci.close()

