#Script to analyze multiple data and calculate variance of % of packets received

import sys
import array
import math
from os import listdir
from os.path import isfile, join
import numpy

sys.stdout = open('standardDeviations.txt', 'w')

mypath1="Model01/SimulationFiles"
mypath2="Model02/SimulationFiles"
onlyfiles1 = [f for f in listdir(mypath1) if isfile(join(mypath1, f))]
onlyfiles2 = [f for f in listdir(mypath2) if isfile(join(mypath2, f))]

onlyfiles1.sort()
onlyfiles2.sort()

print " "
print "Files inside MWproject are: ", onlyfiles1
print "Files inside MWproject2 are: ", onlyfiles2
print " "

j = 0
elemfiles1 = len(onlyfiles1)
elemfiles2 = len(onlyfiles2)
percentageStd1 = [0.00] * elemfiles1
percentageStd2 = [0.00] * elemfiles2
percentageSin1 = [0.00] * 250
percentageSin2 = [0.00] * 250

#DEVIATIONS IN VERSION01
print " "
print "STANDARD DEVIATIONS FOR VERSION 01"
for elem in range(elemfiles1):
    fileToOpen = mypath1 + "/" + onlyfiles1[elem]
    #print "File to open: ", fileToOpen
    f = open(fileToOpen, "r")
    lines = f.readlines()
    i = 0
    for line in lines:
        s = line.split()
        if( len(s) > 6 ):
            if ( s[6] == "%" ):
                percentageSin1[i] = round(float(s[5]),2)
                #print "PercentageSin[", i, "] = ", percentageSin[i]
                i += 1
    #print "Array of single variances: ", percentageSin1
    percentageStd1[elem] = round(float(numpy.std(percentageSin1)),2)
    j += 1
    print "Standard deviation: ", percentageStd1[elem], " of file ", fileToOpen
print " "
      
#DEVIATIONS OF VERSION02
print " "
print "STANDARD DEVIATIONS FOR VERSIONS 02"
for elem in range(elemfiles2):
    fileToOpen = mypath2 + "/" + onlyfiles2[elem]
    #print "File to open: ", fileToOpen
    f = open(fileToOpen, "r")
    lines = f.readlines()
    i = 0
    for line in lines:
        s = line.split()
        if( len(s) > 6 ):
            if ( s[6] == "%" ):
                percentageSin2[i] = round(float(s[5]),2)
                #print "PercentageSin[", i, "] = ", percentageSin[i]
                i += 1
    #print "Array of single variances: ", percentageSin2
    percentageStd2[elem] = round(float(numpy.std(percentageSin2)),2)
    j += 1
    print "Standard deviation: ", percentageStd2[elem], " of file ", fileToOpen
      






