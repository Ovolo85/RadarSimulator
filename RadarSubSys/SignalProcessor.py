from UtilityFunctions import calculateMUR, calculateMUV, calculateClutterVel


class SignalProcessor:
    
    
    def __init__(self, m, n, rangeGateSize, dopplerBinSize, maxRangeGate, prfs, noOfDopplerBins, highestClosingVel):
        self.m = m
        self.n = n
        self.rangeGateSize = rangeGateSize
        self.dopplerBinSize = dopplerBinSize
        self.maxRangeGate = maxRangeGate
        self.prfs = prfs
        self.noOfDopplerBins = noOfDopplerBins
        self.highestClosingVel = highestClosingVel
        self.highestOpeningVel = highestClosingVel - (noOfDopplerBins * dopplerBinSize)
        self.lowestPositiveDopplerBin = int(abs(self.highestOpeningVel) / dopplerBinSize)

        self.initPrfMurTable()
        self.resolutionIntervalAlarmLists = []
        self.lastBurstDetectionList = []

        self.resiDetectionReportList = []
        
    def initPrfMurTable(self):
        self.prfMurTable = []
        for prf in self.prfs:
            self.prfMurTable.append({"prf":prf, "mur":calculateMUR(prf)})

    def processBurst(self, echoes, prf, frequency, velocity, azimuth, elevation):
        
        burstAlarmList = []

        # Get Muv and Mur
        # TODO: implement Channels to get a fixed library of MUVs
        muv = calculateMUV(self.prfs[prf], frequency)
        mur = self.prfMurTable[prf]["mur"]

        # Get Clutter Velocity
        # TODO: VC seems correct, now filter the Echoes with it
        V_c = calculateClutterVel(azimuth, elevation, velocity)
        
        # Range and Doppler Unfold
        if len(echoes) > 0:
            
            for echo in echoes:
                rangeCandidates = []
                rangeGateCandidates = []
                velCandidates = []
                velBinCandidates = []

                rangeCandidates.append(echo[0])
                rangeGateCandidates.append(int(echo[0]/self.rangeGateSize))
                velCandidates.append(echo[1])
                velBinCandidates.append(int(echo[1]/self.dopplerBinSize) + self.lowestPositiveDopplerBin)

                rangeCandidate = echo[0]
                rangeCandidate += mur
                while rangeCandidate < self.maxRangeGate*self.rangeGateSize:
                    rangeCandidates.append(rangeCandidate)
                    rangeGateCandidates.append(int(rangeCandidate/self.rangeGateSize))
                    rangeCandidate += mur

                velCandidate = echo[1]
                velCandidate -= muv
                while velCandidate > self.highestOpeningVel:
                    velCandidates.append(velCandidate)
                    velBinCandidates.append(int(velCandidate/self.dopplerBinSize) + self.lowestPositiveDopplerBin -1)
                    velCandidate -= muv

                velCandidate = echo[1]
                velCandidate += muv
                while velCandidate < self.highestClosingVel:
                    velCandidates.append(velCandidate)
                    velBinCandidates.append(int(velCandidate/self.dopplerBinSize) + self.lowestPositiveDopplerBin)
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


                        

                            
                        







    