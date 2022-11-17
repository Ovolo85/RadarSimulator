import json
import math
from numpy import mod
from UtilityFunctions import calculateMUR, calculateMUV, calculateClutterVel


class SignalProcessor:
    
    
    def __init__(self, radarDataFile):
        
        self.getRadarDataFromJSON(radarDataFile)
        
        
        self.highestOpeningVelocity = self.highestClosingVelocity - (self.numberOfDopplerBins * self.dopplerBinSize)

        self.lowestPositiveDopplerBin = int(abs(self.highestOpeningVelocity) / self.dopplerBinSize) + 1  # Doppler bin 0 - 10 m/s if Bin size = 10

        self.initPrfMurTable()
        self.resolutionIntervalAlarmLists = []
        self.lastBurstDetectionList = []

        self.resiDetectionReportList = []
        
    def initPrfMurTable(self):
        self.prfMurTable = []
        for prf in self.prfs:
            self.prfMurTable.append({"prf":prf, "mur":calculateMUR(prf)})

    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)
        
        self.m = data["M"]
        self.n = data["N"]
        
        self.prfs = data["PRFs"]

        self.rangeGateSize = data["RangeGateSize"]
        self.dopplerBinSize = data["DopplerBinSize"]
        self.maxRangeGate = data["MaxRangeGate"]
        self.numberOfDopplerBins = data["NumberOfDopplerBins"]
        self.highestClosingVelocity = data["HighestClosingVelocity"]

        self.MBCNotchActive = data["MBCNotchActive"]
        self.MBCNotchType = data["MBCNotchType"]
        self.MBCHalfWidthInBins = data["MBCHalfWidthInBins"]

    def processBurst(self, echoes, prf, frequency, velocity, azimuth, elevation):
        
        burstAlarmList = []
        internalEchoesList = echoes

        # Get Muv and Mur
        # TODO: implement Channels to get a fixed library of MUVs
        muv = calculateMUV(self.prfs[prf], frequency)
        mur = self.prfMurTable[prf]["mur"]

        # Get Clutter Velocity
        
        V_c = calculateClutterVel(azimuth, elevation, velocity)
        ambiguousV_c = mod(V_c, muv)
        ambiguousV_cDopplerBin = math.floor(ambiguousV_c/self.dopplerBinSize) + self.lowestPositiveDopplerBin
        
        # Perform MBC Filtering
        if self.MBCNotchActive:
            if self.MBCNotchType == "static":
                for i, echo in enumerate(internalEchoesList):
                    ambiguousEchoDopplerBin = math.floor(echo[1]/self.dopplerBinSize) + self.lowestPositiveDopplerBin
                    if abs( ambiguousEchoDopplerBin - ambiguousV_cDopplerBin) <= self.MBCHalfWidthInBins:
                        internalEchoesList.pop(i)
                        print("MBC Echo Filtered")
            else:
                print("Unknown Type of MBC Filtering selected.")

        # Range and Doppler Unfold
        if len(internalEchoesList) > 0:
            
            for echo in internalEchoesList:
                rangeCandidates = []
                rangeGateCandidates = []
                velCandidates = []
                velBinCandidates = []

                rangeCandidates.append(echo[0])
                rangeGateCandidates.append(int(echo[0]/self.rangeGateSize))
                velCandidates.append(echo[1])
                # TODO: Encapsulate the transition from RR to Doppler Bin in a Function
                velBinCandidates.append(math.floor(echo[1]/self.dopplerBinSize) + self.lowestPositiveDopplerBin)

                # Range Unfold
                rangeCandidate = echo[0]
                rangeCandidate += mur
                while rangeCandidate < self.maxRangeGate*self.rangeGateSize:
                    rangeCandidates.append(rangeCandidate)
                    rangeGateCandidates.append(int(rangeCandidate/self.rangeGateSize))
                    rangeCandidate += mur

                # Doppler Unfold
                velCandidate = echo[1]
                velCandidate -= muv
                while velCandidate > self.highestOpeningVelocity:
                    velCandidates.append(velCandidate)
                    velBinCandidates.append(math.floor(velCandidate/self.dopplerBinSize) + self.lowestPositiveDopplerBin)
                    velCandidate -= muv

                velCandidate = echo[1]
                velCandidate += muv
                while velCandidate < self.highestClosingVelocity:
                    velCandidates.append(velCandidate)
                    velBinCandidates.append(math.floor(velCandidate/self.dopplerBinSize) + self.lowestPositiveDopplerBin)
                    velCandidate += muv
                
                burstAlarmList.append([])
                burstAlarmList[-1].append(rangeGateCandidates)
                burstAlarmList[-1].append(velBinCandidates)                
                
        
        # Construct RESI Alarm List, contains the last N Burst Alarm Lists
        self.resolutionIntervalAlarmLists.append(burstAlarmList)
        if len(self.resolutionIntervalAlarmLists) > self.n:
            self.resolutionIntervalAlarmLists.pop(0)

        # M/N Processing
        rangeGateAlarmCounter = []
        burstDetectionList = []
        potentialBurstDetectionList = []
        

        if len(self.resolutionIntervalAlarmLists) == self.n:
            for alarm in self.resolutionIntervalAlarmLists[-1]: # Alarms from last Burst
                for rangeGate in alarm[0]:                      # alarm = [[Ranges][RRs]]
                    rangeGateAlarmCounter.append(1)
                    for previousBurst in range(self.n - 1):
                        for previousAlarm in self.resolutionIntervalAlarmLists[previousBurst]:
                            for previousRangeGate in previousAlarm[0]:
                                if previousRangeGate == rangeGate:
                                    rangeGateAlarmCounter[-1] += 1
                    
                for i in range(len(rangeGateAlarmCounter)):
                    if rangeGateAlarmCounter[i] >= self.m:
                        potentialBurstDetectionList.append(alarm[0][i])
                        # TODO: This might be the spot to figure out the RR
            
            for idx, potDet in enumerate(potentialBurstDetectionList):
                for prevDetList in self.resiDetectionReportList:
                    for prevDet in prevDetList: 
                        if prevDet == potDet:
                            potentialBurstDetectionList.pop(idx)

            self.resiDetectionReportList.append(potentialBurstDetectionList)
            if len(self.resiDetectionReportList) > self.n:
                self.resiDetectionReportList.pop(0)

        return potentialBurstDetectionList, V_c


                        

                            
                        







    