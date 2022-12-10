import json
import math
from numpy import mod
from UtilityFunctions import calculateMUR, calculateMUV, calculateClutterVel, calculateLowestPositiveDopplerBin


class SignalProcessor:
    
    
    def __init__(self, radarDataFile):
        
        self.getRadarDataFromJSON(radarDataFile)
        
        
        self.highestOpeningVelocity = self.highestClosingVelocity - (self.numberOfDopplerBins * self.dopplerBinSize)

        self.lowestPositiveDopplerBin = calculateLowestPositiveDopplerBin(self.highestOpeningVelocity, self.dopplerBinSize)  # Doppler bin 0 - 10 m/s if Bin size = 10

        self.initPrfMurTable()
        
        self.resiAlarmLists = []
        self.resiDetectionReportList = []
        
        #self.lastBurstDetectionList = []

        
        
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

        self.dopplerBinIntegrationTolerance = data["DopplerBinIntegrationTolerance"]
        self.rangeGateIntegrationTolerance = data["RangeGateIntegrationTolerance"]

        self.MBCNotchActive = data["MBCNotchActive"]
        self.MBCNotchType = data["MBCNotchType"]
        self.MBCHalfWidthInBins = data["MBCHalfWidthInBins"]

    def processBurst(self, echoes, prf, frequency, velocity, azimuth, elevation):
    # Measure a single Burst and report Range, Range Rate and Monopuls values
    # echoes:       A LIST of all echoes from that burst [[R, RR, AzMP, ElMp], [], ...] --> Note that R and RR are ambiguous
    # prf:          An INT pointing into the PRF List from Radar.JSON
    # frequency:    Hz
    # velocity:     Ownship Velocity
    # azimuth:      Antenna Angle in Reference to Boresight
    # elevation:    Antenna Angle 


        burstAlarmList = []
        burstAlarmListAnalogue = []
        filteredEchoesList = []
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
                        filteredEchoesList.append(echo)
                        internalEchoesList.pop(i)
            else:
                print("Unknown Type of MBC Filtering selected.")

        # Range and Doppler Unfold
        # This translates the "Echo" to an "Alarm"
        # Echo:     [R, RR, AzMP, ElMp]
        # Alarm:    [[R1, R2, ...], [RR1, RR2, ...], AzMP, ElMp]
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
                
                # Digitized Alarm List for SIP internal M/N Processing
                burstAlarmList.append([])
                burstAlarmList[-1].append(rangeGateCandidates)
                burstAlarmList[-1].append(velBinCandidates) 
                burstAlarmList[-1].append(echo[2]) # Az Monopulse
                burstAlarmList[-1].append(echo[3]) # El Monopulse

                # Non-Digitized List purely for Visualization
                burstAlarmListAnalogue.append([])
                burstAlarmListAnalogue[-1].append(rangeCandidates)
                burstAlarmListAnalogue[-1].append(velCandidates)
                
        # Construct RESI Alarm List, contains the last N Burst Alarm Lists
        # Alarm:                [[R1, R2, ...], [RR1, RR2, ...], AzMP, ElMp]
        # Burst Alarm List:     A List of ALarms
        # RESI Alarm List:      A List of Lists of Alarms
        self.resiAlarmLists.append(burstAlarmList)
        if len(self.resiAlarmLists) > self.n:
            self.resiAlarmLists.pop(0)

        # M/N Processing
        potentialBurstDetectionList = []
        
        if len(self.resiAlarmLists) == self.n:
            for alarm in self.resiAlarmLists[-1]: # Alarms from current Burst
                
                rangeGateAlarmCounter = []
                dopplerBinAlarmCounter = []

                for rangeGate in alarm[0]:                      # alarm = [[Ranges][RRs]]
                    rangeGateAlarmCounter.append(1)
                    for previousBurst in range(self.n - 1):
                        for previousAlarm in self.resiAlarmLists[previousBurst]:
                            for previousRangeGate in previousAlarm[0]:
                                if abs(previousRangeGate - rangeGate) <= self.rangeGateIntegrationTolerance:
                                    rangeGateAlarmCounter[-1] += 1
                    
                for i in range(len(rangeGateAlarmCounter)):
                    if rangeGateAlarmCounter[i] >= self.m:
                        
                        # Range Rate Check
                        for dopplerBin in alarm[1]:
                            dopplerBinAlarmCounter.append(1)
                            for previousBurst in range(self.n -1):
                                for previousAlarm in self.resiAlarmLists[previousBurst]:
                                    for previousDopplerBin in previousAlarm[1]:
                                        if abs(previousDopplerBin - dopplerBin) <= self.dopplerBinIntegrationTolerance:
                                            dopplerBinAlarmCounter[-1] += 1

                        potentialDopplerBinFound = False
                        potentialDopplerBin = None
                        
                        for idx, dopplerBinCount in enumerate(dopplerBinAlarmCounter):
                            if dopplerBinCount >= self.m: 
                                if not potentialDopplerBinFound:
                                    potentialDopplerBinFound = True
                                    potentialDopplerBin = alarm[1][idx]
                                else:
                                    print("RR set to None due to Ambiguity")
                                    potentialDopplerBin = None
                                    break
                        
                        # Prepare Output Detection List
                        potentialBurstDetectionList.append([alarm[0][i], potentialDopplerBin, alarm[2], alarm[3]])

            
            # Remove Detections already reported within resolution interval
            # TODO: Still double reports, possibly due to RG Jumps in neighboring RCs
            for idx, potDet in enumerate(potentialBurstDetectionList):
                for prevDetList in self.resiDetectionReportList:
                    for prevDet in prevDetList: 
                        if prevDet[0] == potDet[0]:
                            potentialBurstDetectionList.pop(idx)

            self.resiDetectionReportList.append(potentialBurstDetectionList)
            if len(self.resiDetectionReportList) > self.n:
                self.resiDetectionReportList.pop(0)

        # TODO: Returning a "Potential" List seems odd
        return potentialBurstDetectionList, V_c, filteredEchoesList, burstAlarmListAnalogue


                        

                            
                        







    