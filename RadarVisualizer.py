import matplotlib.pyplot as plt
#from mpldatacursor import datacursor
import numpy as np
import json
from UtilityFunctions import *

class RadarVisualizer:

    def __init__(self, radarDataFile, simDataFile):
        self.getRadarDataFromJSON(radarDataFile)
        self.getSimDataFromJson(simDataFile)
        self.symboltable = ["ro", "go", "bo", "co", "mo", "yo", "ko", "wo"]
    
    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        self.prfs = data["PRFs"]
        self.burstLength = data["BurstLength"]
        self.pw = data["PulseWidth"]

    def getSimDataFromJson(self, simDataFile):
        with open(simDataFile) as json_file:
            data = json.load(json_file)
        self.maxRange = data["MaxRange"]

    # Scenario Plots (Truth Data)

    def plotCompleteScenarioTopDown(self, scenario):
        # first entry is Ownship data, all others are the targets
        arrayToPlot = np.array(scenario[0])
        
        plt.figure()
        plt.plot(arrayToPlot[:,2], arrayToPlot[:,1])

        for i in range(len(scenario) -1):
            arrayToPlot = np.array(scenario[i + 1])
            plt.plot(arrayToPlot[:,2], arrayToPlot[:,1])
        
        ax = plt.gca() #you first need to get the axis handle
        ax.set_aspect(1) #sets the height to width ratio to 1

        plt.title("Scenario Top-Down View")
        plt.xlabel("East [m]")
        plt.ylabel("North [m]")

        plt.grid(True)

        plt.show()

    def plotTargetScenarioTopDown(self, scenario):
        
        plt.figure()

        # first entry is Ownship data, all others are the targets
        for i in range(len(scenario) -1):
            arrayToPlot = np.array(scenario[i + 1])
            plt.plot(arrayToPlot[:,2], arrayToPlot[:,1], label="Target " + str(i+1))
            plt.legend(loc="upper right")
        
        ax = plt.gca() #you first need to get the axis handle
        ax.set_aspect(1) #sets the height to width ratio to 1

        plt.title("Targets Top-Down View")
        plt.xlabel("East [m]")
        plt.ylabel("North [m]")

        plt.grid(True)

        plt.show()

    def plotAllTargetRanges(self, scenario):
        plt.figure()
        for target in range(1, len(scenario)):
            ranges = []
            
            for position in scenario[target]:
                ownshipPosition = []
                for ownshipPositionCandidate in scenario[0]:
                    if (ownshipPositionCandidate[0] - position[0]) < (self.burstLength / 100):
                        ownshipPosition = ownshipPositionCandidate
                        break
                ranges.append([position[0], vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))])
            rangesToPlot = np.array(ranges)
            plt.plot(rangesToPlot[:,0], rangesToPlot[:,1])

        plt.grid(True)

        plt.show()

    def plotSingleTargetRange(self, scenario, tgtNo):
        plt.figure()

        targetData = scenario[tgtNo]
        ranges = []

        for position in targetData:
            ownshipPosition = []
            for ownshipPositionCandidate in scenario[0]:
                if (ownshipPositionCandidate[0] - position[0]) < (self.burstLength / 100):
                    ownshipPosition = ownshipPositionCandidate
                    break
            ranges.append([position[0], vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))])
        rangesToPlot = np.array(ranges)
        plt.plot(rangesToPlot[:,0], rangesToPlot[:,1])

        plt.title("Target " + str(tgtNo) + " Range")
        plt.grid(True)

        plt.show()

    # Setting Plots

    def plotEclipsingZones(self):
        
        plt.figure()
        numberOfPRFs = len(self.prfs)
        
        currentRow = 1
        for prf in self.prfs:
            prfRange = []
            mur = calculateMUR(prf)
            pwInMeter = self.pw * c
            for r in range(self.maxRange):
                if np.mod(r, mur+pwInMeter) < pwInMeter:
                    prfRange.append(1)
                else:
                    prfRange.append(0)
            plt.subplot(numberOfPRFs, 1, currentRow)
            plt.plot(prfRange)
            currentRow += 1
        plt.show()


   
    # Simulation Plots

    def plotAntennaMovement(self, antennaAngles):
        
        arrayToPlot = np.array(antennaAngles)

        plt.figure()

        plt.subplot(211)
        plt.plot(arrayToPlot[:,0], arrayToPlot[:,2])
        plt.title("Antenna Elevation")
        plt.grid(True)

        plt.subplot(212)
        plt.plot(arrayToPlot[:,0], arrayToPlot[:,1])
        plt.title("Antenna Azimuth")
        plt.grid(True)
        

        plt.show()

    def plotEchoRanges (self, echoes):
        arrayAllPRFs = np.array(echoes)
        
        plt.figure()

        for prf in range(len(self.prfs)):
            filter_array = []
            for echo in arrayAllPRFs:
                if echo[1] == prf:
                    filter_array.append(True)
                else:
                    filter_array.append(False)
            arrayToPlot = arrayAllPRFs[filter_array]
            plt.plot(arrayToPlot[:,0], arrayToPlot[:,2], self.symboltable[prf], label=self.prfs[prf])

        plt.legend(loc="upper right")
        plt.title("RF Echoes - Ambiguous Range over Time")
        plt.grid(True)
        plt.show()


        



    