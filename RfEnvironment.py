import json

from numpy import mod
import numpy as np
from UtilityFunctions import *

class RfEnvironment:
    
    def __init__(self, scenario, simulationSettingFile, radarFile) -> None:
        self.scenario = scenario
        self.getSimulationSettingFromJSON(simulationSettingFile)
        self.getRadarDataFromJSON(radarFile)

    def measure(self, frq, prf, pw, az, el, time):
        
        # TODO: Implement Resolution criteria

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

        ownshipHeading = ownshipPositionAtTime[4]
        ownshipVelocity = ownshipPositionAtTime[5]
        ownshipPitch = ownshipPositionAtTime[6]

        for target in range(len(targetPositionsAtTime)):
            toTargetVector = vectorOwnshipToTarget(ownshipPositionAtTime, targetPositionsAtTime[target])
            
            targetHeading = targetPositionsAtTime[target][4]
            targetVelocity = targetPositionsAtTime[target][5]
            targetPitch = targetPositionsAtTime[target][6]
            
            offBoresightAngle = angleBetweenVectors(toTargetVector, antennaPointingVector)
            if offBoresightAngle < (self.beamWidth+self.beamOverlap) / 2:
                
                # TODO: calculate Monopuls
                # TODO: Introduce MBC Returns               

                # Range, RangeRate, DiffAz, DiffEl
                measuredRange = vectorToRange(toTargetVector)
                targetSightline = northEastDown2AzElRange(toTargetVector[0], toTargetVector[1], toTargetVector[2])
                measuredRangeRate = calculateRangeRate(targetSightline[0], targetSightline[1], ownshipHeading, ownshipPitch, ownshipVelocity, targetHeading, targetPitch, targetVelocity)
                if measuredRange < self.maxRange:
                    if self.measurementNoise:
                        measuredRange = measuredRange + np.random.normal(0.0, self.rangeStandardDeviation)
                        measuredRangeRate = measuredRangeRate + np.random.normal(0.0, self.velocityStandardDeviation)
                    
                    # Get Ambiguous Values by MUR and MUV
                    measuredRange = mod(measuredRange, calculateMUR(prf))
                    measuredRangeRate = mod(measuredRangeRate, calculateMUV(prf, frq))
                    
                    if self.eclipsingEnabled:
                        if measuredRange > calculateEclipsingZoneSize(pw):
                            burstEchoes.append([measuredRange, measuredRangeRate, 0.0, 0.0])
                        
                    else:
                        burstEchoes.append([measuredRange, measuredRangeRate, 0.0, 0.0])
        return burstEchoes
        
    # TODO: Maybe this would better be located in a "Ownship" Simulation? Instead of RF Environment...
    def getOwnshipSpeed(self, time):
        timeStep = round(time / self.burstLength)
        return self.scenario[0][timeStep][5]

    def getSimulationSettingFromJSON(self, simulationSettingFile):
        with open(simulationSettingFile) as json_file:
            data = json.load(json_file)
        self.measurementNoise = data["MeasurementNoise"]
        self.eclipsingEnabled = data["RangeEclipsing"]
        self.maxRange = data["MaxRange"]
        self.beamOverlap = data["BeamOverlap"]

    def getRadarDataFromJSON(self, radarFile):
        with open(radarFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
        self.beamWidth = data["BeamWidth"]
        self.rangeStandardDeviation = data["RangeStandardDeviation"]
        self.velocityStandardDeviation = data["VelocityStandardDeviation"]