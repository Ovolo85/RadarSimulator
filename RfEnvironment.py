import json

from numpy import mod
import numpy as np
from UtilityFunctions import *

class RfEnvironment:
    
    def __init__(self, scenario, simulationSettingFile, radarFile) -> None:
        self.scenario = scenario
        self.getSimulationSettingFromJSON(simulationSettingFile)
        self.getRadarDataFromJSON(radarFile)

    def measure(self, prf, pw, az, el, time):
        
        burstEchoes = []

        targetPositionsAtTime = []
        for target in range(len(self.scenario)-1):
            targetStartTime = self.scenario[target+1][0][0]
            if targetStartTime <= time:
                timeFromTargetStartTime = time - targetStartTime
                targetPositionRow = round(timeFromTargetStartTime / self.burstLength)
                if targetPositionRow < len(self.scenario[target+1]):
                    targetPositionsAtTime.append(self.scenario[target+1][targetPositionRow])

        ownshipPositionAtTime = self.scenario[0][round(time / self.burstLength)]
        antennaHeading = mod(az + ownshipPositionAtTime[4], 360)
        antennaPointingVector = azElRange2NorthEastDown(antennaHeading, el, 1000)

        for target in range(len(targetPositionsAtTime)):
            toTargetVector = vectorOwnshipToTarget(ownshipPositionAtTime, targetPositionsAtTime[target])
            
            offBoresightAngle = angleBetweenVectors(toTargetVector, antennaPointingVector)
            if offBoresightAngle < (self.beamWidth+0.2) / 2:
                #print("Detection at time " + str(time) + " against Target " + str(target) +  " with OffBoresight of " + str (offBoresightAngle))
                # TODO: calculate RR; Monopuls
                # Range, RangeRate, DiffAz, DiffEl
                measuredRange = vectorToRange(toTargetVector)
                if self.measurementNoise:
                    measuredRange = measuredRange + np.random.normal(0.0, self.rangeStandardDeviation)
                burstEchoes.append([measuredRange, 0.0, 0.0, 0.0])

        return burstEchoes
        

    def getSimulationSettingFromJSON(self, simulationSettingFile):
        with open(simulationSettingFile) as json_file:
            data = json.load(json_file)
        self.measurementNoise = data["MeasurementNoise"]
        self.eclipsingEnabled = data["RangeEclipsing"]

    def getRadarDataFromJSON(self, radarFile):
        with open(radarFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
        self.beamWidth = data["BeamWidth"]
        self.rangeStandardDeviation = data["RangeStandardDeviation"]