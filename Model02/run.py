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
import array
from TOSSIM import *
#from simcore import *

#simulation variable
t = Tossim([])
#sf = SerialForwarder(9001)
#throttle = Throttle(t,10)
#sf_throttle=True
#sf_process=True

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

#Creating Nodes manually
#for i in range (0,3):
#    print "Creating node: ", i
#    node1 = t.getNode(i)
#    time1 = (1)*t.ticksPerSecond()
#    node1.bootAtTime(time1)
#    print "I'll boot at time: ", time1/t.ticksPerSecond(), "[sec]

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
            t.getNode(int(s[1])).addNoiseTraceReading(float(s[2]))
            t.getNode(int(s[1])).addNoiseTraceReading(float(s[3]))
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

#Only if we hve to use the serial port
'''
if (sf_process == True):
    sf.process()
if (sf_throttle == True):
    throttle.initialize()

for i in range(0,50000):
    t.runNextEvent()
    if (sf_throttle == True):
        throttle.checkThrottle()
    if (sf_process == True):
        sf.process()
'''

for i in range(10000):
	t.runNextEvent()
	#print "Value of i: ", i  


print "@@@ SIMULATION FINESHED @@@"
#throttle.printStatistics()

'''
print "-----> SIMULATION STATISTICS: "
print "Packets sent by node 0 (SINK)"
print packets[0]
'''

#DATA ANALYSIS
sys.stdout = open('testData.txt', 'w')
packetCount = [0]* nodeNumber

outputData = "testOut.txt"
f = open(outputData, "r")
lines = f.readlines()
for line in lines:
    s = line.split()
    if( len(s) > 3):
        if( s[2] == "SENT" ):
            print "---------------------START LINE ----"
            print "Argument 0: ", s[0]
            print "Argument 1: ", s[1]
            print "Argument 2: ", s[2]
            print "Argument 3: ", s[3]
            print "Argument 4: ", s[4]
            packetCount[int(s[4])] += 1
            print "---------------------END LINE -----"

for i in range(0, nodeNumber):
    print "Packet sent by node ", i, ": ", packetCount[i]





















