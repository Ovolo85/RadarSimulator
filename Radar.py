import json
import matplotlib.pyplot as plt
from numpy import array
from RadarSubSys.Receiver import Receiver

from RadarSubSys.Scanner import Scanner
from RadarSubSys.SignalProcessor import SignalProcessor
from RadarSubSys.Tracker import Tracker

class Radar:
    ## Main Class of the Radar Simulator
    
    def __init__(self, radarDataFile, radarSettingFile, rfEnvironment):
        
        self.getRadarDataFromJSON(radarDataFile)
        self.getRadarSettingFromJSON(radarSettingFile)
        
        
        self.scanner = Scanner(self.beamwidth, self.scanCenter, self.scanHalfWidth, self.scanBars, self.scanSpeed)
        self.sip = SignalProcessor(self.m, self.n, self.rangeGateSize, self.dopplerBinSize, self.maxRangeGate)
        self.tracker = Tracker()
        self.receiver = Receiver(self.prfs, self.pulseWidth, rfEnvironment)

        # Lists for Simulation Results
        self.antennaAngles = []
        self.echoes = []
        self.barTimes = []

    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
        self.measurementSigma = data["MeasurementSigma"]
        self.m = data["M"]
        self.n = data["N"]
        self.beamwidth = data["BeamWidth"]
        self.scanSpeed = data["ScanSpeed"]
        self.turnAroundTime = data["TurnAroundTime"]
        self.pulseWidth = data["PulseWidth"]
        self.prfs = data["PRFs"]
        self.rangeGateSize = data["RangeGateSize"]
        self.dopplerBinSize = data["DopplerBinSize"]
        self.maxRangeGate = data["MaxRangeGate"]

    def getRadarSettingFromJSON(self,radarSettingFile):
        with open(radarSettingFile) as json_file:
            data = json.load(json_file)
        self.scanCenter = data["ScanCenter"]
        self.scanHalfWidth = data["ScanHalfWidth"]
        self.scanBars = data["ScanBars"]

    

    def operate(self, runtime):
        time = 0.0
        nextTurnAround = False
        turnAroundStartTime = 0.0
        barStartTime = 0.0
        currentBar = 1

        self.antennaAngles.append([time, self.scanner.getAzimuth(), self.scanner.getElevation(), self.scanner.getBar()])

        while time < runtime:
            if not nextTurnAround:
                az, el, bar = self.scanner.moveScanner(self.burstLength)
                echoesFromBurst = self.receiver.measureBurst(az, el, time)
                for echo in echoesFromBurst: 
                    self.echoes.append([time, echo[0], echo[1], echo[2], echo[3]])

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

        
        
        return {"AntennaAngles" : self.antennaAngles, "Echoes":self.echoes, "BarTimes":self.barTimes}

        
        
    
