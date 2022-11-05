from UtilityFunctions import calculateMUR, calculateMUV


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

        self.simStep = 0

    def initPrfMurTable(self):
        self.prfMurTable = []
        for prf in self.prfs:
            self.prfMurTable.append({"prf":prf, "mur":calculateMUR(prf)})

    def processBurst(self, echoes, prf, frequency):
        
        burstAlarmList = []

        self.simStep += 1
        
        # Initialize a new R/D Matrix
        #rd = [[False]*self.maxRangeGate for _ in range(self.noOfDopplerBins)]
        #print("RD Mat done " + str(self.simStep))

        # Get Muv and Mur
        # TODO: implement Channels to get a fixed library of MUVs
        muv = calculateMUV(self.prfs[prf], frequency)
        mur = self.prfMurTable[prf]["mur"]
        
        # Process Echoes to resolve ambiguities 
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
               
                burstAlarmList.append(rangeGateCandidates)
                burstAlarmList.append(velBinCandidates)                
                print("Echo processed")


        
        # Construct RESI
        self.resolutionIntervalAlarmLists.append(burstAlarmList)
        if len(self.resolutionIntervalAlarmLists) > self.n:
            self.resolutionIntervalAlarmLists.pop(0)






    