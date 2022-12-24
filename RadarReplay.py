import pygame
import json
import sys
import numpy as np

class RadarReplay:

    def __init__(self, replayDataFile, radarDataFile, radarSettingsFile, simResults) -> None:
        pygame.init()

        self.getReplayDataFromJSON(replayDataFile)
        self.getRadarDataFromJSON(radarDataFile)
        self.getRadarSettingsFromJSON(radarSettingsFile)

        self.pixelPerDegree = self.size[0] / (self.gimbalLimits * 2)

        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption('Radar Tracker Testbed - B-Scope Replay')

        self.prepareData(simResults)

        self.run()
       
    def run(self):
        
        
        running = True
        frame = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
            
            self.screen.fill(self.backgroundColor)

            self.drawBackground()
            self.drawAntennaPosition(frame)
            self.drawPlots(frame)

            font = pygame.font.SysFont(None, 22)
            rangeScaleText = font.render(str(self.rangeScale), True, self.textColor)
            self.screen.blit(rangeScaleText, (10, 10))

            pygame.display.flip()

            frame += 1
            if frame >= len(self.antennaDataInFramrerate[:,0]):
                running = False

            self.clock.tick(self.framerate)

        pygame.quit()

    def drawAntennaPosition(self, frame):
        # TODO: From Time to Time there is a jump in Antenna Position
        antennaAzScreenPos = (self.antennaDataInFramrerate[frame][1] + self.gimbalLimits) * (self.pixelPerDegree)
        pygame.draw.line(self.screen,self.scannerColor, (antennaAzScreenPos, 0), (antennaAzScreenPos, self.size[1]))

    def drawBackground(self):
        leftScanLimit = self.getAzimuthInPixel(-self.scanHalfWidth)
        rightScanLimit = self.getAzimuthInPixel(self.scanHalfWidth)
        middleLine = self.getAzimuthInPixel(0)

        pygame.draw.line(self.screen,self.scanBorderColor, (leftScanLimit, 0), (leftScanLimit, self.size[1]))
        pygame.draw.line(self.screen,self.scanBorderColor, (rightScanLimit, 0), (rightScanLimit, self.size[1]))
        pygame.draw.line(self.screen,self.scanBorderColor, (middleLine, 0), (middleLine, self.size[1]))

        pygame.draw.line(self.screen, self.scanGridColor, (leftScanLimit, int(self.size[0]/4)), (rightScanLimit, int(self.size[0]/4)))
        pygame.draw.line(self.screen, self.scanGridColor, (leftScanLimit, int(self.size[0]/2)), (rightScanLimit, int(self.size[0]/2)))
        pygame.draw.line(self.screen, self.scanGridColor, (leftScanLimit, int(self.size[0]/4*3)), (rightScanLimit, int(self.size[0]/4*3)))
        
    def drawPlots(self, frame):
        if self.plotDataInFrameRate[frame] != None:
            for plot in self.plotDataInFrameRate[frame]:
                plotAzPosition = self.getAzimuthInPixel(plot[1]) - (plot[2] / 2)
                plotRangePosition = self.getRangeInPixel(plot[0]) - (plot[2] / 2)
                pygame.draw.rect(self.screen, self.plotColor, [plotAzPosition, plotRangePosition, plot[2], plot[2]])

    def getAzimuthInPixel(self, az):
        middlePx = self.size[0] / 2
        return int(middlePx + (az * self.pixelPerDegree))  

    def getRangeInPixel(self, r):
        rangeValInPixel = r/self.rangeScale * self.size[1]
        return int(self.size[1] - rangeValInPixel)
                  

    def prepareData(self, simResult):
        
        # Antenna Data
        antennaDataInput = np.array(simResult["AntennaAngles"])
        antennaDataInFramerateTime = np.arange(0, antennaDataInput[-1][0], 1/self.framerate)
        self.antennaDataInFramrerate = np.interp(antennaDataInFramerateTime, antennaDataInput[:,0], antennaDataInput[:,1])

        self.antennaDataInFramrerate = np.vstack((antennaDataInFramerateTime, self.antennaDataInFramrerate)).T

        # Plots
        plotSizes = [1, 0.75, 0.5, 0.25, 0]
        
        self.plotDataInFrameRate = [None] * len(self.antennaDataInFramrerate[:,0])
        numberOfFramesPerPlot = self.plotLifeTime * self.framerate
        numberOfFramesPerPlotSizeLevel = int(numberOfFramesPerPlot / 4)
        sizeLevelFrameCounter = 0
        
        for idx, detection in enumerate(simResult["DetectionReports"]):
            currentPlotSizeLevel = 0
            frameOfDetection = int(detection[0] * self.framerate) + 1 # One Frame Later
            azimuth = (detection[3] - simResult["OwnshipNEDatDetection"][idx][4]) % 360
            if azimuth > 180:
                azimuth -= 360
            for i in range(numberOfFramesPerPlot):
                # TODO: Compensate Plot Position for Ownship Movement and RR
                sizeLevelFrameCounter += 1
                if sizeLevelFrameCounter > numberOfFramesPerPlotSizeLevel:
                    currentPlotSizeLevel += 1
                    sizeLevelFrameCounter = 0
                if self.plotDataInFrameRate[frameOfDetection + i] == None:
                    self.plotDataInFrameRate[frameOfDetection + i] = [[detection[1], azimuth, int(self.plotInitialSize * plotSizes[currentPlotSizeLevel])]]
                else:
                    self.plotDataInFrameRate[frameOfDetection + i].append([detection[1], azimuth, int(self.plotInitialSize * plotSizes[currentPlotSizeLevel])])

    def getReplayDataFromJSON(self, replayDataFile):
        with open(replayDataFile) as json_file:
            data = json.load(json_file)

        self.size = data["Size"]
        self.framerate = data["Framerate"]

        self.rangeScale = data["RangeScale"]

        self.plotLifeTime = data["PlotLifeTime"]
        self.plotInitialSize = data["PlotInitialSize"]

        self.scannerColor = data["ScannerColor"]
        self.backgroundColor = data["BackgroundColor"]
        self.scanBorderColor = data["ScanBorderColor"]
        self.scanGridColor = data["ScanGridColor"]
        self.plotColor = data["PlotColor"]
        self.textColor = data["TextColor"]

    def getRadarDataFromJSON(self, radarDataFile):
        with open(radarDataFile) as json_file:
            data = json.load(json_file)

        self.gimbalLimits = data["GimbalLimits"]

    def getRadarSettingsFromJSON(self, radarSettingsFile):
        with open(radarSettingsFile) as json_file:
            data = json.load(json_file)

        self.scanCenter = data["ScanCenter"]
        self.scanHalfWidth = data["ScanHalfWidth"]

if __name__ == "__main__":
    a = RadarReplay("replay.json")
