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

        self.initPrfMurTable()
        self.resolutionIntervalRDMatrices = []

        self.simStep = 0

    def initPrfMurTable(self):
        self.prfMurTable = []
        for prf in self.prfs:
            self.prfMurTable.append({"prf":prf, "mur":calculateMUR(prf)})

    def processBurst(self, echoes, prf, frequency):
        
        self.simStep += 1
        
        # Initialize a new R/D Matrix
        #rd = [[False]*self.maxRangeGate for _ in range(self.noOfDopplerBins)]
        #print("RD Mat done " + str(self.simStep))

        # Get Muv and Mur
        muv = calculateMUV(self.prfs[prf], frequency)
        mur = self.prfMurTable[prf]["mur"]
        
        # Process Echoes to resolve ambiguities 
        if len(echoes) > 0:
            
            for echo in echoes:
                pass
        
        # Construct RESI
        #self.resolutionIntervalRDMatrices.append(rd)
        if len(self.resolutionIntervalRDMatrices) > self.n:
            self.resolutionIntervalRDMatrices.pop(0)






    