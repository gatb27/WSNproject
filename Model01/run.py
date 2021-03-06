print "********************************"
print "********************************"
print "                                "
print "        TOSSIM SCRIPT           "
print "                                "
print "********************************"
print "********************************"

import sys
import time
import math
import numpy as np
import array
from TOSSIM import *
from tinyos.tossim.TossimApp import *

#simulation variable
n = NescApp()
t = Tossim(n.variables.variables())

#Import file .out create with -> java net.tinyos.sim.LinkLayerModel config.txt
topology="topology.out"
modelfile="linkgain.out"
nodeNumber=0

print "Initializing mac...."
mac = t.mac()
print "Initializing radio channels...."
radio = t.radio()
print "Iniatializing simulator..."
t.init()

sys.stdout = open('testOut.txt', 'w')
out = sys.stdout

print "Activate debug message on channel test"
t.addChannel("test", out)
t.addChannel("boot", out)
t.addChannel("sink", out)
t.addChannel("radio_pack", out)
t.addChannel("recv", out)
t.addChannel("forw", out)
t.addChannel("timer", out)

#Create nodes looking at topology.out file
f = open(topology, "r")
lines = f.readlines()
for line in lines:
    s = line.split()
    if (len(s) > 0):
        nodeNumber = nodeNumber + 1
        print "Creating node: ", s[0]
        m = t.getNode(int(s[0]))
        bootime = (1)*t.ticksPerSecond()
        m.bootAtTime(bootime)
        print "I'll boot at time: ", bootime/t.ticksPerSecond(), "[sec]"

#Add a link for each couple created inside linkgain.out file
f = open(modelfile, "r")
lines = f.readlines()
for line in lines:
    s = line.split()
    if (len(s) > 0):
        if (s[0] == "gain"):
            print "Setting radio channel from node ", s[1], " to node ", s[2], " with gain ", s[3], "dBm"
            radio.add(int(s[1]), int(s[2]), float(s[3]))

#Adding Noise Trace Reading using meyer-heavy
meyer = open("meyer-heavy.txt", "r")
for line in meyer:
  s = line.strip()
  if s:
    val = int(s)
    for i in range(0, nodeNumber):
      t.getNode(i).addNoiseTraceReading(val)

'''
#Add noise model looking at linkgain.out file
f = open(modelfile, "r")
lines = f.readlines()
for line in lines:
    s = line.split()
    if (len(s) > 0):
        if (s[0] == "noise"):
            t.getNode(int(s[1])).addNoiseTraceReading(val)
            #t.getNode(int(s[1])).addNoiseTraceReading(vall)
'''

'''
#Create noise model
noisemodel = open(modelfile, "r")
lines = noisemodel.readlines()
for line in lines:
    s = line.split()
    nod = int(s[1])
    if(s[0] == "noise"):
        print "Creating noise model for ", nod
        t.getNode(nod).createNoiseModel()
'''

for i in range (0, nodeNumber):
    print "@@@@@@ Creating noise model for node: ", i
    t.getNode(i).createNoiseModel()


#We can now start the TOSSIM SIMULATION
print "----------------------------------------------"
print "                                              "
print "      START TOSSIM SIMULATION PART            "
print "                                              "
print "----------------------------------------------"

m = t.getNode(24)
v = m.getVariable("FloodingPartC.sinkCounter")
counter = v.getData()

'''
for i in range(30000):
    t.runNextEvent()
'''

while (counter < 251):
    t.runNextEvent()
    counter = v.getData()
    if(counter==250):
        print "250 Packets were sent by the SINK"

print "@@@ SIMULATION FINESHED @@@"
#throttle.printStatistics()


#DATA ANALYSIS
sys.stdout = open('testData.txt', 'w')
packetSent = [0] * nodeNumber
packetRecv = [0] * nodeNumber
totalPackets = 0


outputData = "testOut.txt"
f = open(outputData, "r")
lines = f.readlines()
for line in lines:
    s = line.split()
    if( len(s) > 3):
        if( s[2] == "SENT" ):
            #print "---------------------START LINE ----"
            #print "Argument 0: ", s[0]
            #print "Argument 1: ", s[1]
            #print "Argument 2: ", s[2]
            #print "Argument 3: ", s[3]
            #print "Argument 4: ", s[4]
            packetSent[int(s[4])] += 1
        if( s[2] == "RECV" ):
            packetRecv[int(s[4])] += 1
            #print "---------------------END LINE -----"

for i in range(0, nodeNumber):
    print "Packet sent by node ", i, ": ", packetSent[i]
    print "Packet recv by node ", i, ": ", packetRecv[i]
    totalPackets = totalPackets + packetSent[i]


recv = np.array([ [0 for y in range(nodeNumber)] for x in range(packetSent[24]) ])
np.set_printoptions(threshold=np.nan)
for line in lines:
    s = line.split()
    if( len(s) > 3):        
        if( s[2] == "RECV" ):
            #print "Argument 0: ", s[0]
            #print "Argument 1: ", s[1]
            #print "Argument 2: ", s[2]
            #print "Argument 3: ", s[3]
            #print "Argument 4: ", s[4]
            #print "Argument 5: ", s[5]
            #print "Argument 6: ", s[6]
            recv[int(s[6])][int(s[4])] = 1
print recv


print ""
print "------------------DATA ANALYSIS -------------------------"
print "Number of packets used to flood the network: ", totalPackets
print "                                                               "

print "Percentage of node that actually received the flooded data"

percentageRecv = np.array([0]*packetSent[24], np.float16)
for i in range(packetSent[24]):
    for j in range(nodeNumber):
        #print recv[i][j]
        percentageRecv[i] = percentageRecv[i] + recv[i][j]
    percentageRecv[i] = ( percentageRecv[i] / (nodeNumber-1) ) * 100
    percentageRecv[i] = round(float(percentageRecv[i]),2)
    print "Packet ", i, " was received by: ", percentageRecv[i], "% of nodes"

#standardDev = 0.00
#standardDev = round(float(np.std(percentageRecv)),2)
#print "Standard Deviation is: ", standardDev

sumPerc = 0
for i in range(packetSent[24]):
    sumPerc = sumPerc + percentageRecv[i]
sumPerc = sumPerc / packetSent[24]
print "                                                               "
print "-------------------- PERCENTAGE -------------------------------"
print "The percentage of nodes that have received the data is: ", sumPerc, "%"
print "                                                               "






















