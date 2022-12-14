import matplotlib
from matplotlib.backend_bases import NavigationToolbar2
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
#from mpldatacursor import datacursor
import numpy as np
import json
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from UtilityFunctions import *

class RadarVisualizer:

    def __init__(self, radarDataFile, simDataFile):
        self.getRadarDataFromJSON(radarDataFile)
        self.getSimDataFromJson(simDataFile)
        self.symboltable = ["ro", "go", "bo", "co", "mo", "yo", "ko", "rx"]
    
    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        
        self.prfs = data["PRFs"]
        self.burstLength = data["BurstLength"]
        self.n = data["N"]
        self.pw = data["PulseWidth"]

        self.dopplerBinSize = data["DopplerBinSize"]
        self.rangeGateSize = data["RangeGateSize"]

        self.numberOfDopplerBins = data["NumberOfDopplerBins"]
        self.highestClosingVelocity = data["HighestClosingVelocity"]

        self.MBCNotchActive = data["MBCNotchActive"]
        self.MBCNotchType = data["MBCNotchType"]
        self.MBCHalfWidthInBins = data["MBCHalfWidthInBins"]

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

    def plotTargetScenarioTopDownAndDetectionReports(self, scenario, detectionReports, ownshipNEDatDetection, newWin):
        
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        for i, target in enumerate(scenario[1:]):
            arrayToPlot = np.array(target)
            ax.plot(arrayToPlot[:,2], arrayToPlot[:,1], label="Target " + str(i+1))
            

        detectionsNE = []
        for i, detection in enumerate(detectionReports):
            rangeInPlane = np.cos(deg2rad(detection[4])) * detection[1]
            north = np.cos(deg2rad(detection[3])) * rangeInPlane
            north = north + ownshipNEDatDetection[i][1]
            east = np.sin(deg2rad(detection[3])) * rangeInPlane
            east = east + ownshipNEDatDetection[i][2]
            detectionsNE.append([north, east])

        arrayToPlot = np.array(detectionsNE)
        ax.plot(arrayToPlot[:,1], arrayToPlot[:,0], "ro", label="Detections")

        ax.legend(loc="upper right")

        canvas = FigureCanvasTkAgg(figure, newWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, newWin)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ax.set_title("Detection Reports - North/East")
        ax.grid()

    def plotAllTargetRanges(self, scenario):
        plt.figure()
        
        for target in range(1, len(scenario)):
            targetStartTime = scenario[target][0][0]
            ownshipRowOffset = round(targetStartTime / self.burstLength)
            
            ranges = []
            
            for idx, position in enumerate(scenario[target]):
                ownshipPosition = scenario[0][idx + ownshipRowOffset]
                ranges.append([position[0], vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))])
                
            rangesToPlot = np.array(ranges)
            plt.plot(rangesToPlot[:,0], rangesToPlot[:,1])

        plt.grid(True)

        plt.show()

    def plotSingleTargetRange(self, scenario, tgtNo):
        plt.figure()

        targetData = scenario[tgtNo]
        targetStartTime = scenario[tgtNo][0][0]
        ownshipRowOffset = round(targetStartTime / self.burstLength)

        ranges = []

        for idx, position in enumerate(targetData):
            ownshipPosition = scenario[0][idx + ownshipRowOffset]
            ranges.append([position[0], vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))])

        rangesToPlot = np.array(ranges)
        plt.plot(rangesToPlot[:,0], rangesToPlot[:,1])

        plt.title("Target " + str(tgtNo) + " Range")
        plt.grid(True)

        plt.show()

    def plotAllTargetRangeRatesAndDetectionReports(self, scenario, detectionReports):
        plt.figure()
        # TODO: This only plots one RR Truth Data, seemingly for the last Tgt
        for target in range(1, len(scenario)):
            targetStartTime = scenario[target][0][0]
            ownshipRowOffset = round(targetStartTime / self.burstLength)
            
            ranges = []
            rangeRates = []
            clutterVelocitiesInSightline = []
            
            for idx, position in enumerate(scenario[target]):
                ownshipPosition = scenario[0][idx + ownshipRowOffset]

                r = vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))

                sightline = vectorOwnshipToTarget(ownshipPosition, position)
                sightlineSpherical = northEastDown2AzElRange(sightline[0], sightline[1], sightline[2])
                rangeRate = calculateRangeRate(sightlineSpherical[0], sightlineSpherical[1], 
                    ownshipPosition[4], ownshipPosition[6], ownshipPosition[5],
                    position[4], position[6], position[5])
                
                rangeRates.append([position[0], rangeRate])
                clutterVelocitiesInSightline.append([position[0], calculateClutterVel(sightlineSpherical[0], sightlineSpherical[1], ownshipPosition[5])])
                ranges.append([position[0], r])
        
        r_arr = np.array(ranges)
        r_arr_diff = np.diff(r_arr[:, 1]) / self.burstLength

        rangeRatesToPlot = np.array(rangeRates)
        detectionReportRRsToPlot = np.array(detectionReports)
        clutterVelocitiesToPlot = np.array(clutterVelocitiesInSightline)
        clutterVelocitiesToPlotMax = clutterVelocitiesToPlot[:,1] + self.MBCHalfWidthInBins * self.dopplerBinSize + self.dopplerBinSize/2
        clutterVelocitiesToPlotMin = clutterVelocitiesToPlot[:,1] - self.MBCHalfWidthInBins * self.dopplerBinSize - self.dopplerBinSize/2

        plt.plot(rangeRatesToPlot[:,0], rangeRatesToPlot[:,1], label="True RR")
        plt.plot(detectionReportRRsToPlot[:,0], detectionReportRRsToPlot[:,2], "ro", label="Detection Report RR")
        plt.plot(clutterVelocitiesToPlot[:,0], clutterVelocitiesToPlot[:,1], label="Expected MBC RR")
        plt.plot(clutterVelocitiesToPlot[:, 0], clutterVelocitiesToPlotMax, "--")
        plt.plot(clutterVelocitiesToPlot[:, 0], clutterVelocitiesToPlotMin, "--")

        # A Testplot whicht alternatively retrieves the RRs from the Position Delta
        # plt.plot(r_arr[0:-1, 0], r_arr_diff, label="Ranges Diff")

        plt.title("Range Rates - Truth Data vs Detection Reports incl. MBC Vc")

        plt.legend(loc="upper right")
        plt.grid()
        plt.show()
            
            


    def plotAllTargetRangesAndDetectionReports(self, scenario, detectionReports):
        plt.figure()
        
        # Truth Data
        for target in range(1, len(scenario)):
            targetStartTime = scenario[target][0][0]
            ownshipRowOffset = round(targetStartTime / self.burstLength)
            
            ranges = []
            for idx, position in enumerate(scenario[target]):
                ownshipPosition = scenario[0][idx + ownshipRowOffset]
                ranges.append([position[0], vectorToRange(vectorOwnshipToTarget(ownshipPosition, position))])


            rangesToPlot = np.array(ranges)
            plt.plot(rangesToPlot[:,0], rangesToPlot[:,1])

        # Detection Reports
        arrayDetectionReports = np.array(detectionReports)
        plt.plot(arrayDetectionReports[:,0], arrayDetectionReports[:,1], "ro")

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
        
        print(matplotlib.get_backend())

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

    # TODO: change all plot functions to this new style
    def plotClutterVelocities(self, clutterVelocities, newWin):
        
        vcArray = np.array(clutterVelocities)
        
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(vcArray[:,0], vcArray[:,1])

        canvas = FigureCanvasTkAgg(figure, newWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, newWin)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ax.set_title("Clutter Velocities - V_C")
        ax.grid()

    def plotAmbiguousRangeDopplerMatrixOfDetection(self, simResult, detNo, newWin):
        
        resiEchoes = []
        echoRow = 0

        detReportTime = simResult["DetectionReports"][detNo-1][0]
        for idx, echo in enumerate(simResult["Echoes"]):
            if echo[0] == detReportTime:
                echoRow = idx
                resiEchoes.append(echo)

        beginOfResiFound = False
        while not beginOfResiFound:
            echoRow -= 1
            if echoRow >= 0: 
                if detReportTime - simResult["Echoes"][echoRow][0] < ((self.n - 1) * self.burstLength + self.burstLength / 10):
                    resiEchoes.append(simResult["Echoes"][echoRow])
                else:
                    break
            else:
                break
                
        figure = Figure(figsize=(7, 4), dpi=100)
        ax = figure.add_subplot(111)
        
        symbol = 0
        for echo in resiEchoes:
            ax.plot(echo[2], echo[3], self.symboltable[symbol], label= "[" + str(echo[1]) + "] " + str(self.prfs[echo[1]]))
            symbol += 1

        ax.legend(loc="upper right")
        ax.xaxis.set_label_text("Range [m]")
        ax.yaxis.set_label_text("Range Rate [m/s]")

        canvas = FigureCanvasTkAgg(figure, newWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, newWin)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ax.set_title("Ambiguous R/D Matrix of Echoes of Detection " + str(detNo) + " (Including MBC Echoes)")
        ax.grid()
        
    def plotRangeUnfoldOfEchoesOfDetection(self, simResult, detNo, newWin):
        
        resiAlarms = []
        alarmRow = 0
        detReportTime = simResult["DetectionReports"][detNo-1][0]

        for idx, alarm in enumerate(simResult["AnalogueAlarms"]):
            if alarm[0] == detReportTime:
                alarmRow = idx
                resiAlarms.append(alarm)
        
        beginOfResiFound = False
        while not beginOfResiFound:
            alarmRow -= 1
            if alarmRow >= 0: 
                if detReportTime - simResult["AnalogueAlarms"][alarmRow][0] < ((self.n - 1) * self.burstLength + self.burstLength / 10):
                    resiAlarms.append(simResult["AnalogueAlarms"][alarmRow])
                else:
                    break
            else:
                break
        
        figure = Figure(figsize=(14, 8), dpi=100)
        ax = figure.add_subplot(111)

        symbol = 0
        
        for alarm in resiAlarms:
            alarmRDMat = []
            for rangeAlarm in alarm[2]:
                for dopplerAlarm in alarm[3]:
                    alarmRDMat.append([rangeAlarm, dopplerAlarm])
            
            arrayToPlot = np.array(alarmRDMat)

            ax.plot(arrayToPlot[:,0], arrayToPlot[:,1], self.symboltable[symbol], label= "[" + str(alarm[1]) + "] " + str(self.prfs[alarm[1]]))
            symbol += 1

        ax.legend(loc="upper right")
        ax.xaxis.set_label_text("Range [m]")
        ax.yaxis.set_label_text("Range Rate [m/s]")
        

        rangeTicks = np.arange(0, self.maxRange, self.rangeGateSize * 100)
        rangeGateTicks = np.arange(0, self.maxRange, self.rangeGateSize)

        dopplerTicks = np.arange(self.highestClosingVelocity - self.dopplerBinSize*self.numberOfDopplerBins, self.highestClosingVelocity, self.dopplerBinSize * 50)
        dopplerBinTicks = np.arange(self.highestClosingVelocity - self.dopplerBinSize*self.numberOfDopplerBins, self.highestClosingVelocity, self.dopplerBinSize)

        ax.set_xticks(rangeTicks)
        ax.set_xticks(rangeGateTicks, minor=True)
        ax.set_yticks(dopplerTicks)
        ax.set_yticks(dopplerBinTicks, minor=True)

        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        canvas = FigureCanvasTkAgg(figure, newWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, newWin)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ax.set_title("Range/Doppler Unfold of Detection " + str(detNo))
        



    