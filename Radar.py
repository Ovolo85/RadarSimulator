import json
import matplotlib.pyplot as plt
from numpy import array

from RadarSubSys.Receiver import Receiver
from RadarSubSys.Scanner import Scanner
from RadarSubSys.SignalProcessor import SignalProcessor
from RadarSubSys.Tracker import Tracker

from UtilityFunctions import calculateLowestPositiveDopplerBin

class Radar:
    ## Main Class of the Radar Simulator
    # TODO: We might have some issues with Euler Angles from time to time...

    def __init__(self, radarDataFile, radarSettingFile, rfEnvironment):
        
        self.getRadarDataFromJSON(radarDataFile)
        self.getRadarSettingFromJSON(radarSettingFile)
        
        
        self.scanner = Scanner(self.beamwidth, self.scanCenter, self.scanHalfWidth, self.scanBars, self.scanSpeed)
        self.sip = SignalProcessor(radarDataFile)
        self.tracker = Tracker()
        self.receiver = Receiver(self.carrierFrequency, self.frequencyAgility, self.prfs, self.pulseWidth, rfEnvironment)
        
        self.rfEnvironment = rfEnvironment
        
        # Lists for Simulation Results
        self.antennaAngles = []
        self.echoes = []
        self.barTimes = []
        self.barsWithDetections = []
        self.detectionReports = []
        self.clutterVelocities = []
        self.highestOpeningVelocity = self.highestClosingVelocity - (self.numberOfDopplerBins * self.dopplerBinSize)
        self.lowestPositiveDopplerBin = calculateLowestPositiveDopplerBin(self.highestOpeningVelocity, self.dopplerBinSize)

    # TODO: Most of the data from the JSONs is no longer needed here because it is read in by the subsystems on their own
    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
        self.m = data["M"]
        self.n = data["N"]
        self.beamwidth = data["BeamWidth"]
        self.scanSpeed = data["ScanSpeed"]
        self.turnAroundTime = data["TurnAroundTime"]
        self.carrierFrequency = data["CarrierFrequency"]
        self.pulseWidth = data["PulseWidth"]
        self.prfs = data["PRFs"]
        self.rangeGateSize = data["RangeGateSize"]
        self.dopplerBinSize = data["DopplerBinSize"]
        self.maxRangeGate = data["MaxRangeGate"]
        self.numberOfDopplerBins = data["NumberOfDopplerBins"]
        self.highestClosingVelocity = data["HighestClosingVelocity"]

    def getRadarSettingFromJSON(self,radarSettingFile):
        with open(radarSettingFile) as json_file:
            data = json.load(json_file)
        self.scanCenter = data["ScanCenter"]
        self.scanHalfWidth = data["ScanHalfWidth"]
        self.scanBars = data["ScanBars"]
        self.frequencyAgility = data["FrequencyAgility"]

    def appendToEchoList(self, time, prf, echolistFromMeasurement):
        for echo in echolistFromMeasurement:
            self.echoes.append([time, prf, echo[0], echo[1], echo[2], echo[3]])
    
    def appendToDetectionList(self, time, detectionsFromBurst):
        for detectionR_RR in detectionsFromBurst:
            detectionRange = detectionR_RR[0] * self.rangeGateSize + self.rangeGateSize/2
            if not detectionR_RR[1] == None:
                detectionRangeRate = (detectionR_RR[1] - self.lowestPositiveDopplerBin) * self.dopplerBinSize + self.dopplerBinSize/2
            else:
                detectionRangeRate = None
            self.detectionReports.append([time, detectionRange, detectionRangeRate])

    def operate(self, runtime):
        time = 0.0
        nextTurnAround = False
        turnAroundStartTime = 0.0
        barStartTime = 0.0
        currentBar = 1

        self.antennaAngles.append([time, self.scanner.getAzimuth(), self.scanner.getElevation(), self.scanner.getBar()])

        while time < runtime:
            if not nextTurnAround:
                
                # Scanner Movement
                az, el, bar = self.scanner.moveScanner(self.burstLength)
                
                # Receiver
                usedCarrierFrequency, usedPRF, echoesFromBurst = self.receiver.measureBurst(az, el, time)
                self.appendToEchoList(time, usedPRF, echoesFromBurst)
                
                # Signal Processor
                ownshipSpeed = self.rfEnvironment.getOwnshipSpeed(time)
                detectionList, clutterVelocity = self.sip.processBurst(echoesFromBurst, usedPRF, usedCarrierFrequency, ownshipSpeed, az, el)
                if len(detectionList) > 0:
                    
                    if not self.barsWithDetections.__contains__(currentBar):
                        self.barsWithDetections.append([currentBar])
                self.appendToDetectionList(time, detectionList)
                self.clutterVelocities.append([time, clutterVelocity])

                # Turn Around Management
                if az == self.scanHalfWidth + self.scanCenter[0]:
                    nextTurnAround = True
                    turnAroundStartTime = time
                    self.barTimes.append([currentBar, barStartTime, time])
            else:
                if time - turnAroundStartTime >= self.turnAroundTime:
                    self.scanner.turnAround()
                    nextTurnAround = False
                    currentBar += 1
                    barStartTime = time

            time += self.burstLength
            self.antennaAngles.append([time, az, el, bar])

        
        
        return {"AntennaAnglesHeader" : ["time", "Azimuth", "Elevation", "Bar"], "AntennaAngles" : self.antennaAngles, 
        "EchoesHeader":["time", "PRF", "Range", "RangeRate", "Monopuls Az", "Monopuls El"], "Echoes":self.echoes, 
        "BarTimesHeader": ["BarNumber", "StartTime", "EndTime"], "BarTimes":self.barTimes, 
        "BarsWithDetectionsHeader": ["BarNumber"], "BarsWithDetections":self.barsWithDetections, 
        "DetectionReportsHeader": ["time", "Range", "RangeRate"], "DetectionReports": self.detectionReports,
        "ClutterVelocitiesHeader": ["time", "ClutterVelocity"], "ClutterVelocities": self.clutterVelocities}

        
        
    
