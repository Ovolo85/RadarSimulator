import matplotlib.pyplot as plt
from numpy import array

class RadarVisualizer:

    def __init__(self):
        pass

    def plotCompleteScenarioTopDown(self, scenario):
        # first entry is Ownship data, all others are the targets
        arrayToPlot = array(scenario[0])
        
        plt.figure()
        plt.plot(arrayToPlot[:,1], arrayToPlot[:,0])

        for i in range(len(scenario) -1):
            arrayToPlot = array(scenario[i + 1])
            plt.plot(arrayToPlot[:,1], arrayToPlot[:,0])
        
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
            plt.plot(arrayToPlot[:,1], arrayToPlot[:,0])
        
        ax = plt.gca() #you first need to get the axis handle
        ax.set_aspect(1) #sets the height to width ratio to 1

        plt.title("Targets Top-Down View")
        plt.xlabel("East [m]")
        plt.ylabel("North [m]")

        plt.grid(True)

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

    