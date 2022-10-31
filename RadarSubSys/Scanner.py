class Scanner:
    
    def __init__(self, beamWidth, scanCenter, halfwidth, bars, speed):
        self.beamWidth = beamWidth
        self.scanCenter = scanCenter
        self.halfWidth = halfwidth
        self.bars = bars
        self.speed = speed

        self.azimuth = self.getStartOfBarAzimuth()
        self.elevation = self.getStartOfFrameElevation()

        self.currentBar = 1
        
        

    def moveScanner(self, deltaTime):
        self.azimuth += deltaTime * self.speed
        if self.azimuth > self.halfWidth + self.scanCenter[0]:
            self.azimuth = self.halfWidth + self.scanCenter[0]
        
        return [self.azimuth, self.elevation, self.currentBar]
        

    def turnAround(self):
        if self.currentBar < self.bars:
            self.currentBar += 1
            self.elevation += self.beamWidth
        else:
            self.currentBar = 1
            self.elevation = self.getStartOfFrameElevation()
        self.azimuth = self.getStartOfBarAzimuth()

    def getStartOfFrameElevation(self):
        return - (self.bars - 1) * (self.beamWidth / 2) + self.scanCenter[1]

    def getStartOfBarAzimuth(self):
        return -self.halfWidth + self.scanCenter[0]

    def setBars(self, number):
        self.bars = number

    def setHalfwidth(self, degree):
        self.halfWidth = degree

    def setScanCenter(self, center):
        self.scanCenter = center

    def getAzimuth(self):
        return self.azimuth

    def getElevation(self):
        return self.elevation

    def getBar(self):
        return self.currentBar

