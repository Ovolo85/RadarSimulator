import json
import time


from OutputStore import OutputStore
from Ownship import Ownship
from Radar import Radar
from DataStore import DataStore 
from RadarVisualizer import RadarVisualizer
from RfEnvironment import RfEnvironment
from ScenarioInterpolator import ScenarioInterpolator
from ScenarioProcessor import ScenarioProcessor
from InputHandler import InputHandler

from PyQt5.QtWidgets import QPlainTextEdit


class SimulationHandler():
    def __init__(self, dataStore : DataStore) -> None:
        self.dataStore = dataStore
        self.outputStore = OutputStore()
        self.inputHandler = InputHandler(self.dataStore)
        
        self.scenarioProcessor = ScenarioProcessor()

        self.simulationPerformed = False

    def startSimulation(self, output : QPlainTextEdit, simFromJSON = True):
        
        # PROCESS the scenario
        if simFromJSON:
            #-----vvv-----
            self.scenario, ownshipExtended, tspiDataNames = self.scenarioProcessor.processScenario(self.dataStore.getScenarioFile(), self.dataStore.getScenarioProcSettingFile())
            #-----^^^-----
            output.insertPlainText("Scenario " + self.dataStore.getScenarioFile() + " processed...\n")
            self.outputAircraftTimesFromScenario(output)
            if ownshipExtended:
                output.insertPlainText("NOTE: Ownship data had to be extended to cover Tgt Lifetime!\n")
            
            # Save TSPI data in SimSteps
            self.outputStore.writeTSPItoDisk(tspiDataNames, self.scenario)
            output.insertPlainText("TSPI Data saved to disk...\n")

        else:
            #-----vvv-----
            self.scenario = self.inputHandler.readTSPIfromDisk()
            #-----^^^-----

        # INTERPOLATION from SimStep to Radar Burst Length
        scenarioInterpolator = ScenarioInterpolator(self.getBurstLength())
        #-----vvv-----
        self.scenario = scenarioInterpolator.interpolateScenario(self.scenario)
        #-----^^^-----
        output.insertPlainText("TSPI interpolated to Radar Burst Length...\n")

        # Initialize Stuff
        self.rfEnvironment = RfEnvironment(self.scenario, self.dataStore.getSimSettingsFile(), self.dataStore.getRadarFile())
        self.ownship = Ownship(self.scenario, self.dataStore.getRadarFile())
        self.radar = Radar(self.dataStore.getRadarFile(), self.dataStore.getRadarSettingsFile(), self.rfEnvironment, self.ownship)
        self.visualizer = RadarVisualizer(self.dataStore.getRadarFile(), self.dataStore.getSimSettingsFile())
        output.insertPlainText("RF Environment, Ownship, Radar and Visualizer generated...\n")

        # SIMULATE the Radar
        output.insertPlainText("Simulation Started...\n")
        maxOwnshipTime = self.scenario[0][-1][0]
        output.insertPlainText("Simulating " + str(maxOwnshipTime) + "s...\n")
        startTime = time.time()
        #-----vvv-----
        self.simResult = self.radar.operate(maxOwnshipTime)
        #-----^^^-----
        endTime = time.time()
        duration = endTime - startTime
        self.outputSimulationStatusText(duration, output)
        self.outputStore.writeSimResultToDisk(self.simResult)

        self.simulationPerformed = True

    def outputAircraftTimesFromScenario(self, output : QPlainTextEdit):
        osStart = self.scenario[0][0][0]
        osEnd = self.scenario[0][-1][0]
        output.insertPlainText("Ownship data Times: " + str([osStart, osEnd]) + "\n")
        
        targetNo = 1
        for target in range (1, len(self.scenario)):
            output.insertPlainText("Target " + str(targetNo) + " Times: " + str([self.scenario[target][0][0], self.scenario[target][-1][0]]) + "\n")
            targetNo += 1

    def outputSimulationStatusText(self, simtime, output : QPlainTextEdit):
        output.insertPlainText( "Simulation duration: " + str(simtime) + " s\n")
        output.insertPlainText("Scan Bars with Detections: " + str(self.simResult["BarsWithDetections"]) + "\n")
        output.insertPlainText("Detections: 1.." + str(len(self.simResult["DetectionReports"])) + "\n")
        # TODO: log number of bursts required per detection

    def getScenarioData(self):
        return self.scenario
    
    def getNumberOfTargets(self):
        return len(self.scenario)-1
    
    def getVisualizer(self):
        return self.visualizer
    
    def getSimulationPerformed(self):
        return self.simulationPerformed
    
    def getSimResults(self):
        return self.simResult
    
    def getPRFs(self):
        radarDataFile = self.dataStore.getRadarFile()
        with open(radarDataFile) as json_file:
            data = json.load(json_file)

        return data["PRFs"]
    
    def getBurstLength(self):
        radarDataFile = self.dataStore.getRadarFile()
        with open(radarDataFile) as json_file:
            data = json.load(json_file)

        return data["BurstLength"]