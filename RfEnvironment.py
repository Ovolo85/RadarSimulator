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
        
        # Intialize Data Structures
        burstEchoes = []
        rangeEclipsedEchoes = []
        targetPositionsAtTime = []

        # Check the start time of the targets, targetPositionsAtTime will held all target row numbers afterwards
        for target in range(1, len(self.scenario)):
            targetStartTime = self.scenario[target][0][0]
            if targetStartTime <= time:
                timeFromTargetStartTime = time - targetStartTime
                targetPositionRow = round(timeFromTargetStartTime / self.burstLength)
                if targetPositionRow < len(self.scenario[target]):
                    targetPositionsAtTime.append(self.scenario[target][targetPositionRow])

        ownshipPositionAtTime = self.scenario[0][round(time / self.burstLength)]
        
        # Calculate the Antenna Sightline Vector
        antennaHeading = mod(az + ownshipPositionAtTime[4], 360) # correct Antenna Azimuth for Heading
        antennaPointingVector = azElRange2NorthEastDown(antennaHeading, el, 1000)

        ownshipHeading = ownshipPositionAtTime[4]
        ownshipVelocity = ownshipPositionAtTime[5]
        ownshipPitch = ownshipPositionAtTime[6]

        # Test all targets for mainbeam coverage
        for target in range(len(targetPositionsAtTime)):
            
            toTargetVector = vectorOwnshipToTarget(ownshipPositionAtTime, targetPositionsAtTime[target])
            offBoresightAngle = angleBetweenVectors(toTargetVector, antennaPointingVector)
            
            targetHeading = targetPositionsAtTime[target][4]
            targetVelocity = targetPositionsAtTime[target][5]
            targetPitch = targetPositionsAtTime[target][6]
            
            # TODO: Find a better technique to replace the Overlap...
            if offBoresightAngle < (self.beamWidth+self.beamOverlap) / 2:
                
                azMonopulse = calculateAzMonopulse(toTargetVector, antennaPointingVector)
                elMonopulse = calculateElMonopulse(toTargetVector, antennaPointingVector)

                # TODO: Introduce MBC Returns               

                # Range, RangeRate, DiffAz, DiffEl
                measuredRange = vectorToRange(toTargetVector)
                targetSightline = northEastDown2AzElRange(toTargetVector[0], toTargetVector[1], toTargetVector[2])
                measuredRangeRate = calculateRangeRate(targetSightline[0], targetSightline[1], ownshipHeading, ownshipPitch, ownshipVelocity, targetHeading, targetPitch, targetVelocity)
                
                # TODO: Probabilistic approach based on RCS to get max ranges?
                if measuredRange < self.maxRange:
                    if self.measurementNoise:
                        measuredRange = measuredRange + np.random.normal(0.0, self.rangeStandardDeviation)
                        measuredRangeRate = measuredRangeRate + np.random.normal(0.0, self.velocityStandardDeviation)
                        azMonopulse = azMonopulse + np.random.normal(0.0, self.monopulseStandardDeviation)
                        elMonopulse = elMonopulse + np.random.normal(0.0, self.monopulseStandardDeviation)

                    # Get Ambiguous Values by MUR and MUV
                    measuredRange = mod(measuredRange, calculateMUR(prf))
                    measuredRangeRate = mod(measuredRangeRate, calculateMUV(prf, frq))
                    
                    # Filter for eclipsing
                    if self.eclipsingEnabled:
                        if measuredRange > calculateEclipsingZoneSize(pw):
                            burstEchoes.append([measuredRange, measuredRangeRate, azMonopulse, elMonopulse])
                        else:
                            rangeEclipsedEchoes.append([measuredRange, measuredRangeRate, azMonopulse, elMonopulse])
                    else:
                        burstEchoes.append([measuredRange, measuredRangeRate, azMonopulse, elMonopulse])
        
        if self.limitedResolution:
            rangeResolution = calculateRangeResolution(pw)
            rangeResolutionProcessed = False
            
            while not rangeResolutionProcessed:
                echoRemoved = False
                for i, echo in enumerate(burstEchoes):
                    if not echoRemoved:
                        for n, echoToBeCheckedAgainst in enumerate(burstEchoes):
                            if not echoRemoved:
                                if i != n: 
                                    rangeDifference = echo[0] - echoToBeCheckedAgainst[0]
                                    if rangeDifference < rangeResolution and rangeDifference > 0:
                                        
                                        burstEchoes.pop(i)
                                        echoRemoved = True
                if not echoRemoved:
                    rangeResolutionProcessed = True
        
        # resolutionCasesToBeResolved = []
        # if self.limitedResolution and len(burstEchoes > 1):
        #     for i, echo in enumerate(burstEchoes):
                
        #         for n, echoToCheckAgainst in enumerate(burstEchoes):
        #             if i != n:
        #                 if abs(echo[0] - echoToCheckAgainst[0]) <= pw * c / 2:
                            


        return burstEchoes, rangeEclipsedEchoes
        
    

    def getSimulationSettingFromJSON(self, simulationSettingFile):
        with open(simulationSettingFile) as json_file:
            data = json.load(json_file)
        self.measurementNoise = data["MeasurementNoise"]
        self.eclipsingEnabled = data["RangeEclipsing"]
        self.maxRange = data["MaxRange"]
        self.beamOverlap = data["BeamOverlap"]
        self.limitedResolution = data["LimitedResolution"]

    def getRadarDataFromJSON(self, radarFile):
        with open(radarFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
        self.beamWidth = data["BeamWidth"]
        self.rangeStandardDeviation = data["RangeStandardDeviation"]
        self.velocityStandardDeviation = data["VelocityStandardDeviation"]
        self.monopulseStandardDeviation = data["MonopulseStandardDeviation"]