class Scanner:
    
    def __init__(self, beamWidth, scanCenter, halfwidth, bars, speed):
        self.beamWidth = beamWidth
        self.scanCenter = scanCenter
        self.halfWidth = halfwidth
        self.bars = bars
        self.speed = speed

        self.azimuth = -self.halfWidth
        self.elevation = self.getStartOfFrameElevation()

        self.currentBar = 1
        
        

    def moveScanner(self, deltaTime):
        self.azimuth += deltaTime * self.speed
        if self.azimuth > self.halfWidth:
            self.azimuth = self.halfWidth
        
        return [self.azimuth, self.elevation, self.currentBar]
        

    def turnAround(self):
        if self.currentBar < self.bars:
            self.currentBar += 1
            self.elevation += self.beamWidth
        else:
            self.currentBar = 1
            self.elevation = self.getStartOfFrameElevation()
        self.azimuth = -self.halfWidth

    def getStartOfFrameElevation(self):
        return - (self.bars - 1) * (self.beamWidth / 2)

    def setBars(self, number):
        self.bars = number

    def setHalfwidth(self, degree):
        self.halfWidth = degree

    def setScanCenter(self, center):
        self.scanCenter = center

