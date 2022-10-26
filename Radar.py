import json
import matplotlib.pyplot as plt
from numpy import array
from RadarSubSys.Receiver import Receiver

from RadarSubSys.Scanner import Scanner
from RadarSubSys.SignalProcessor import SignalProcessor
from RadarSubSys.Tracker import Tracker

class Radar:
    ## Main Class of the Radar Simulator
    
    def __init__(self, radarDataFile, radarSettingFile, simulationSettingFile, rfEnvironment):
        
        self.getRadarDataFromJSON(radarDataFile)
        self.getRadarSettingFromJSON(radarSettingFile)
        self.getSimulationSettingFromJSON(simulationSettingFile)
        
        self.scanner = Scanner(self.beamwidth, self.scanCenter, self.scanHalfWidth, self.scanBars, self.scanSpeed)
        self.sip = SignalProcessor()
        self.tracker = Tracker()
        self.receiver = Receiver(self.prfs, self.pulseWidth, rfEnvironment)

        self.antennaAngles = []

        pass

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

    def getRadarSettingFromJSON(self,radarSettingFile):
        with open(radarSettingFile) as json_file:
            data = json.load(json_file)
        self.scanCenter = data["ScanCenter"]
        self.scanHalfWidth = data["ScanHalfWidth"]
        self.scanBars = data["ScanBars"]

    def getSimulationSettingFromJSON(self, simulationSettingFile):
        with open(simulationSettingFile) as json_file:
            data = json.load(json_file)
        self.measuremenNoise = data["MeasurementNoise"]

    def operate(self, runtime):
        time = 0.0
        nextTurnAround = False
        turnAroundStartTime = 0.0

        while time < runtime:
            if not nextTurnAround:
                az, el, bar = self.scanner.moveScanner(self.burstLength)
                self.receiver.measureBurst(az, el)
                if az == self.scanHalfWidth:
                    nextTurnAround = True
                    turnAroundStartTime = time
            else:
                if time - turnAroundStartTime >= self.turnAroundTime:
                    self.scanner.turnAround()
                    nextTurnAround = False

            time += self.burstLength
            self.antennaAngles.append([time, az, el, bar])

        
        
        return {"AntennaAngles" : self.antennaAngles}

        
        
    
