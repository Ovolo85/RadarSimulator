import matplotlib.pyplot as plt
from mpldatacursor import datacursor
from numpy import array
import json

class RadarVisualizer:

    def __init__(self, radarDataFile):
        self.getRadarDataFromJSON(radarDataFile)
        self.symboltable = ["ro", "go", "bo", "co", "mo", "yo", "ko", "wo"]
    
    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        self.prfs = data["PRFs"]


    def plotCompleteScenarioTopDown(self, scenario):
        # first entry is Ownship data, all others are the targets
        arrayToPlot = array(scenario[0])
        
        plt.figure()
        plt.plot(arrayToPlot[:,2], arrayToPlot[:,1])

        for i in range(len(scenario) -1):
            arrayToPlot = array(scenario[i + 1])
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
            arrayToPlot = array(scenario[i + 1])
            plt.plot(arrayToPlot[:,2], arrayToPlot[:,1])
        
        ax = plt.gca() #you first need to get the axis handle
        ax.set_aspect(1) #sets the height to width ratio to 1

        plt.title("Targets Top-Down View")
        plt.xlabel("East [m]")
        plt.ylabel("North [m]")

        plt.grid(True)

        plt.show()

    def plotTargetTimeStamps(self, scenario, tgtNo):
        plt.figure()
        arrayToPlot = array(scenario[tgtNo])

        plt.plot(arrayToPlot[:,0])
        plt.show()

    def plotAntennaMovement(self, antennaAngles):
        
        arrayToPlot = array(antennaAngles)

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
        arrayAllPRFs = array(echoes)
        
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


        



    