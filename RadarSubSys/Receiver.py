from operator import mod


class Receiver:

    def __init__(self, prfs, pw, rfEnvironment):
        self.prfs = prfs
        self.pulseWidth = pw

        self.rfEnvironment = rfEnvironment

        self.currentPrf = 0
        self.numberOfPrfs = len(self.prfs)

    def measureBurst(self, az, el, time):
        self.rfEnvironment.measure(self.prfs[self.currentPrf], self.pulseWidth, az, el, time)
        self.currentPrf += 1
        self.currentPrf = mod(self.currentPrf, self.numberOfPrfs)
        pass