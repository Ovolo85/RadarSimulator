from operator import mod

class Receiver:
# This class mainly encapsulates PRF selection.

    # TODO: add a mode design instead of handing over RF parameters in the constructor
    def __init__(self, carrierFrequencies, frequencyAgility,  prfs, pw, rfEnvironment):
        self.carrierFrequencies = carrierFrequencies
        self.frequencyAgility = frequencyAgility
        self.prfs = prfs
        self.pulseWidth = pw

        self.rfEnvironment = rfEnvironment

        self.currentPrf = 0
        self.numberOfPrfs = len(self.prfs)

        self.initFA()

    def initFA(self):
        if self.frequencyAgility == "None":
            self.carrierFrequency = self.carrierFrequencies[0]
        else:
            print("Unknown FA Mode")


    def measureBurst(self, az, el, time):
        #TODO: Burst ID necessary?
        echoes, rangeEclipsedEchoes = self.rfEnvironment.measure(self.carrierFrequency, self.prfs[self.currentPrf], self.pulseWidth, az, el, time)
        usedPrf = self.currentPrf
        self.currentPrf += 1
        self.currentPrf = mod(self.currentPrf, self.numberOfPrfs)
        # TODO: Design Flaw: RangeEclipsedEchoes get now routed through the Radar just to report them for analysis... 
        return [self.carrierFrequency, usedPrf, echoes, rangeEclipsedEchoes]