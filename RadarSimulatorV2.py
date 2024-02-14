import sys, os, time
from sys import platform
import subprocess
from functools import partial
import json

# Qt
from PyQt5.QtWidgets import QComboBox, QPlainTextEdit, QGridLayout, QLineEdit, QMainWindow, QApplication, QPushButton, QWidget, QTabWidget,QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView

# Own Modules
from ScenarioProcessor import ScenarioProcessor
from Ownship import Ownship
from RadarVisualizer import RadarVisualizer
from RfEnvironment import RfEnvironment
from Radar import Radar
from OutputStore import OutputStore
from QTFigureWidget import FigureWidget


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.dataStore = DataStore()
        self.outputStore = OutputStore()
        self.simulationHandler = SimulationHandler(self.dataStore, self.outputStore)

        #--------
        self.title = 'Radar Simulator v2'
        self.left = 0
        self.top = 0
        self.width = 1800    
        self.height = 900
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self, self.dataStore, self.simulationHandler)
        self.setCentralWidget(self.table_widget)
        
        self.show()

class DataStore():
    def __init__(self):
        self.dataLoaded = False

        self.radarFile = ""
        self.radarSettingsFile = ""
        self.simSettingsFile = ""
        self.scenarioProcSettingFile = ""
        self.scenarioFile = ""

    def setSimFiles(self, radar, radarsettings, sim, scenariosettings):
        self.radarFile = radar
        self.radarSettingsFile = radarsettings
        self.simSettingsFile = sim
        self.scenarioProcSettingFile = scenariosettings
        self.dataLoaded = True # TODO: Check if loaded files are valid before setting data loaded state
    
    def setScenarioFile(self, scenario):
        self.scenarioFile = scenario

    def readRadarFileAsText(self):
        with open(self.radarFile,'r') as file:
            return file.read()
    
    def readRadarSettingsFileAsText(self):
        with open(self.radarSettingsFile,'r') as file:
            return file.read()
        
    def readSimSettingsFileAsText(self):
        with open(self.simSettingsFile,'r') as file:
            return file.read()
    
    def readScenarioProcSettingFileAsText(self):
        with open(self.scenarioProcSettingFile,'r') as file:
            return file.read()

    def getRadarFile(self):
        return self.radarFile
    
    def getRadarSettingsFile(self):
        return self.radarSettingsFile
    
    def getSimSettingsFile(self):
        return self.simSettingsFile
    
    def getScenarioFile(self):
        return self.scenarioFile
    
    def getScenarioProcSettingFile(self):
        return self.scenarioProcSettingFile
        
    def getDataLoaded(self):
        return self.dataLoaded

class SimulationHandler():
    def __init__(self, dataStore : DataStore, outputStore : OutputStore) -> None:
        self.dataStore = dataStore
        self.outputStore = outputStore
        
        self.scenarioProcessor = ScenarioProcessor()

        self.simulationPerformed = False

    def startSimulation(self, output : QPlainTextEdit):
        
        self.scenario, ownshipExtended, tspiDataNames = self.scenarioProcessor.processScenario(self.dataStore.getScenarioFile(), self.dataStore.getScenarioProcSettingFile())
        output.insertPlainText("Scenario " + self.dataStore.getScenarioFile() + " processed...\n")
        self.outputAircraftTimesFromScenario(output)
        if ownshipExtended:
            output.insertPlainText("NOTE: Ownship data had to be extended to cover Tgt Lifetime!\n")
        self.outputStore.writeTSPItoDisk(tspiDataNames, self.scenario)
        output.insertPlainText("TSPI Data saved to disk...\n")
        self.rfEnvironment = RfEnvironment(self.scenario, self.dataStore.getSimSettingsFile(), self.dataStore.getRadarFile())
            
        self.ownship = Ownship(self.scenario, self.dataStore.getRadarFile())
        
        self.radar = Radar(self.dataStore.getRadarFile(), self.dataStore.getRadarSettingsFile(), self.rfEnvironment, self.ownship)
        self.visualizer = RadarVisualizer(self.dataStore.getRadarFile(), self.dataStore.getSimSettingsFile())
        
        output.insertPlainText("RF Environment, Ownship, Radar and Visualizer generated...\n")

        output.insertPlainText("Simulation Started...\n")
        maxOwnshipTime = self.scenario[0][-1][0]
        output.insertPlainText("Simulating " + str(maxOwnshipTime) + "s...\n")

        startTime = time.time()
        self.simResult = self.radar.operate(maxOwnshipTime)
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
    

class MyTableWidget(QWidget):
    
    def __init__(self, parent, dataStore, simulationHandler):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
                
        # Add tabs
        self.tabs.addTab(SetupTab(self, dataStore), "Setup")
        startTab = self.tabs.addTab(ScenarioTab(self, dataStore, simulationHandler), "Scenario")
        self.tabs.addTab(PureRadarDataTab(self, simulationHandler), "Pure Radar Data")
        self.tabs.addTab(GeoemtryTab(self, simulationHandler), "Geometry")
        self.tabs.addTab(DetectionTab(self, simulationHandler), "Detections")
        self.tabs.addTab(DetectionPictureTab(self, simulationHandler), "Detection Picture")

        self.tabs.setCurrentIndex(startTab)
        
                
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
class SetupTab(QWidget):
    def __init__(self, parent, dataStore : DataStore):
        super(QWidget, self).__init__(parent)
        
        self.dataStore = dataStore

        self.radarConfigFileLabel = QLabel("Radar Config File")
        self.radarConfigFileName = QLineEdit()
        self.radarConfigFileName.setText("radar.json")
        self.radarConfigFileEditBtn = QPushButton("Edit")
        self.radarConfigFileEditBtn.clicked.connect(partial(self.editFile, self.radarConfigFileName.text()))

        self.radarSettingsFileLabel = QLabel("Radar Settings File")
        self.radarSettingsFileName = QLineEdit()
        self.radarSettingsFileName.setText("radar_setting.json")
        self.radarSettingsFileEditBtn = QPushButton("Edit")
        self.radarSettingsFileEditBtn.clicked.connect(partial(self.editFile, self.radarSettingsFileName.text()))

        self.simulationSettingsFileLabel = QLabel("Simulation Settings File")
        self.simulationSettingsFileName = QLineEdit()
        self.simulationSettingsFileName.setText("sim.json")
        self.simulationSettingsFileEditBtn = QPushButton("Edit")
        self.simulationSettingsFileEditBtn.clicked.connect(partial(self.editFile, self.simulationSettingsFileName.text()))

        self.scenarioProcSettingFileLabel = QLabel("Scenario Processor Settings File")
        self.scenarioProcSettingFileName = QLineEdit()
        self.scenarioProcSettingFileName.setText("scenario_proc_setting.json")
        self.scenarioProcSettingFileEditBtn = QPushButton("Edit")
        self.scenarioProcSettingFileEditBtn.clicked.connect(partial(self.editFile, self.scenarioProcSettingFileName.text()))

        self.loadConfigButton = QPushButton("Load Configuration")
        self.loadConfigButton.clicked.connect(self.loadConfiguration)

        self.outputText = QPlainTextEdit()
        self.outputText.setReadOnly(True)
        
        self.columnsLayout = QGridLayout(self)
        self.gridLayout1 = QGridLayout()
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()
        
        self.gridLayout1.addWidget(self.radarConfigFileLabel,1,1)
        self.gridLayout1.addWidget(self.radarConfigFileName,2,1)
        self.gridLayout1.addWidget(self.radarConfigFileEditBtn, 2, 2)
        
        self.gridLayout1.addWidget(self.radarSettingsFileLabel,3,1)
        self.gridLayout1.addWidget(self.radarSettingsFileName,4,1)
        self.gridLayout1.addWidget(self.radarSettingsFileEditBtn, 4, 2)

        self.gridLayout1.addWidget(self.simulationSettingsFileLabel,5,1)
        self.gridLayout1.addWidget(self.simulationSettingsFileName,6,1)
        self.gridLayout1.addWidget(self.simulationSettingsFileEditBtn, 6, 2)
        
        self.gridLayout1.addWidget(self.scenarioProcSettingFileLabel,7,1)
        self.gridLayout1.addWidget(self.scenarioProcSettingFileName,8,1)
        self.gridLayout1.addWidget(self.scenarioProcSettingFileEditBtn, 8, 2)

        self.layout1.addLayout(self.gridLayout1)
        self.layout1.addWidget(self.loadConfigButton)
        self.layout1.addStretch()

        self.layout2.addWidget(self.outputText)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)

        self.loadConfiguration()

    def loadConfiguration(self):
        radar = self.radarConfigFileName.text()
        radarsettings = self.radarSettingsFileName.text()
        simsettings = self.simulationSettingsFileName.text()
        scenarioprocsettings = self.scenarioProcSettingFileName.text()

        self.dataStore.setSimFiles(radar, radarsettings, simsettings, scenarioprocsettings)

        self.outputText.setPlainText("")

        self.outputText.insertPlainText("RADAR: " + radar + "\n")
        self.outputText.insertPlainText(self.dataStore.readRadarFileAsText() + "\n")
        
        self.outputText.insertPlainText("RADAR SETTINGS: " + radarsettings + "\n")
        self.outputText.insertPlainText(self.dataStore.readRadarSettingsFileAsText() + "\n")

        self.outputText.insertPlainText("SIM SETTINGS: " + simsettings + "\n")
        self.outputText.insertPlainText(self.dataStore.readSimSettingsFileAsText() + "\n")

        self.outputText.insertPlainText("SCENARIO PROCESSOR SETTINGS: " + scenarioprocsettings + "\n")
        self.outputText.insertPlainText(self.dataStore.readScenarioProcSettingFileAsText() + "\n")
    
    def editFile(self, file):
        if platform == "win32":

            subprocess.run(['notepad', file], check=True)

        else:

            subprocess.run(['open', file], check=True)
        
class ScenarioTab(QWidget):
    def __init__(self, parent, datastore : DataStore, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.simulationDone = False

        self.dataStore = datastore
        self.simulationHandler = simulationHandler
        
        self.scenarioFileLabel = QLabel("Scenario File")
        self.scenarioDropDown = QComboBox()
        self.updateScenarioFilesFromFolder()
        self.scenarioDropDown.currentTextChanged.connect(self.selectedScenarioChanged)
        self.updateFolderButton = QPushButton("Update Folder Content")
        self.updateFolderButton.clicked.connect(self.updateScenarioFilesFromFolder)
        self.editScenarioButton = QPushButton("Edit Scenario")
        self.editScenarioButton.clicked.connect(self.editScenario)
        self.startProcessingButton = QPushButton("Start Simulation")
        self.startProcessingButton.clicked.connect(self.startSimulation)
        self.statusOutput = QPlainTextEdit()
        self.statusOutput.setReadOnly(True)
        self.figureSelectionLabel = QLabel("Figure Type")
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Target Scenario N/E", "Complete Scenario N/E", "Target D over Time"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.plotWidget = FigureWidget()

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.layout1.addWidget(self.scenarioFileLabel)
        self.layout1.addWidget(self.scenarioDropDown)
        self.layout1.addWidget(self.updateFolderButton)
        self.layout1.addWidget(self.editScenarioButton)
        self.layout1.addWidget(self.startProcessingButton)
        self.layout1.addWidget(self.statusOutput)
        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        self.layout1.addStretch()

        self.layout2.addWidget(self.plotWidget)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,2)
        self.columnsLayout.setColumnStretch(2,8)

    def updateScenarioFilesFromFolder(self):
        scenariolist =  os.listdir("Scenarios")
        self.scenarioDropDown.clear()
        for s in scenariolist:
            self.scenarioDropDown.addItem(s)

    def selectedScenarioChanged(self):
        self.simulationDone = False
        self.updateFigure()

    def updateFigure(self):
        if self.simulationDone:
            visualizer = self.simulationHandler.getVisualizer()
            if self.figureSelectionDropDown.currentIndex() == 0:
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotTargetScenarioTopDownQT(self.simulationHandler.getScenarioData())
                self.plotWidget.canvas.update_figure_2dim(labels, arraysToPlot, title, xLabel, yLabel, True)
            if self.figureSelectionDropDown.currentIndex() == 1:
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotCompleteScenarioTopDownQT(self.simulationHandler.getScenarioData())
                self.plotWidget.canvas.update_figure_2dim(labels, arraysToPlot, title, xLabel, yLabel, True)
            if self.figureSelectionDropDown.currentIndex() == 2:
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotTargetDownVsTimeQT(self.simulationHandler.getScenarioData())
                self.plotWidget.canvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel)
        else:
            self.plotWidget.canvas.clear_figure()
            self.statusOutput.setPlainText("Please hit \"Start Simulation\" first")

    def startSimulation(self):
        self.statusOutput.setPlainText("")
        if self.dataStore.getDataLoaded() == False:
            self.statusOutput.insertPlainText("ERROR: Please load the Config Files in the Setup Tab first!")
        else: 
            self.dataStore.setScenarioFile("Scenarios/" + self.scenarioDropDown.currentText())
            self.simulationHandler.startSimulation(self.statusOutput)
            
            self.simulationDone = True

            self.updateFigure()

    def editScenario(self):
        file = "Scenarios/" + self.scenarioDropDown.currentText()
        if platform == "win32":
            subprocess.run(['notepad', file], check=True)
        else:
            subprocess.run(['open', file], check=True)

class PureRadarDataTab(QWidget):
    def __init__(self, parent, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.simulationHandler = simulationHandler

        self.figureSelectionLabel = QLabel("Figure Type")
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Eclipsing Zones", "Antenna Angles", "Clutter Velocities", "Ambiguous R/D Matrix"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.prfSelectionLabel = QLabel("PRF")
        self.prfSelectionDropDown = QComboBox()
        prf_names = []
        prfs = self.simulationHandler.getPRFs()
        for idx, p in enumerate(prfs):
            prf_names.append("[" + str(idx) + "] " + str(p) + " Hz")
        self.prfSelectionDropDown.addItems(prf_names)
        self.prfSelectionDropDown.activated.connect(self.updateFigure)

        self.statusOutput = QPlainTextEdit()
        self.statusOutput.setReadOnly(True)

        self.plotWidget = FigureWidget()

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        self.layout1.addWidget(self.prfSelectionLabel)
        self.layout1.addWidget(self.prfSelectionDropDown)
        self.layout1.addWidget(self.statusOutput)

        self.layout1.addStretch()

        self.layout2.addWidget(self.plotWidget)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,2)
        self.columnsLayout.setColumnStretch(2,8)

    def updateFigure(self):
        if self.simulationHandler.getSimulationPerformed():
            if self.figureSelectionDropDown.currentIndex() == 0:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arrayOfArrays, title, xLabels, yLabels = visualizer.plotEclipsingZonesQT()
                self.plotWidget.canvas.update_multi_figure(labels, arrayOfArrays, title, xLabels, yLabels, labelsOff=True)
            if self.figureSelectionDropDown.currentIndex() == 1:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arrayOfArrays, title, xLabels, yLabels = visualizer.plotAntennaMovementQT(self.simulationHandler.getSimResults()["AntennaAngles"])
                self.plotWidget.canvas.update_multi_figure(labels, arrayOfArrays, title, xLabels, yLabels, labelsOff=False)
            if self.figureSelectionDropDown.currentIndex() == 2:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotClutterVelocitiesQT(self.simulationHandler.getSimResults()["ClutterVelocities"])
                self.plotWidget.canvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel)
            if self.figureSelectionDropDown.currentIndex() == 3:
                visualizer = self.simulationHandler.getVisualizer()
                rects, title, xLabel, yLabel, maxR, maxD, minR, minD, mur, muv = visualizer.plotRangeEclipsingAndMBCNotchInRDMatrix(self.prfSelectionDropDown.currentIndex())
                self.plotWidget.canvas.update_figure_rects(rects, title, xLabel, yLabel, maxR, maxD, minR, minD)
                self.statusOutput.setPlainText("MUR: " + str(mur) + "\nMUV: " + str(muv))

        else:
            self.plotWidget.canvas.clear_figure()
            self.statusOutput.setPlainText("Please hit \"Start Simulation\" first")

class GeoemtryTab(QWidget):
    def __init__(self, parent, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.selectedTarget = 0

        #self.dataStore = datastore
        self.simulationHandler = simulationHandler

        self.targetSelectBoxLayout = QGridLayout()
        targetNoLabel = QLabel("TargetNumber")
        self.targetSelectEntry = QLineEdit()
        self.targetSelectBoxLayout.addWidget(targetNoLabel, 1,1)
        self.targetSelectBoxLayout.addWidget(self.targetSelectEntry, 1,2)

        self.setTargetButton = QPushButton("Set Target")
        self.setTargetButton.clicked.connect(self.setTarget)

        self.figureSelectionLabel = QLabel("Figure Type")
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Range to Target", "Target Range Rate", "Target Az/El"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)
        
        self.plotWidget = FigureWidget()

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.layout1.addLayout(self.targetSelectBoxLayout)
        self.layout1.addWidget(self.setTargetButton)
        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        
        self.layout1.addStretch()

        self.layout2.addWidget(self.plotWidget)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,2)
        self.columnsLayout.setColumnStretch(2,8)          
            
    def setTarget(self):
        if self.simulationHandler.getSimulationPerformed() & self.targetSelectEntry.text().isnumeric():
                tgtNo = int(self.targetSelectEntry.text())
                if tgtNo > 0 & tgtNo <= self.simulationHandler.getNumberOfTargets():
                    self.selectedTarget = int(self.targetSelectEntry.text())
                    self.updateFigure()

    def updateFigure(self):
        if self.simulationHandler.getSimulationPerformed():

            visualizer = self.simulationHandler.getVisualizer()

            if self.figureSelectionDropDown.currentIndex() == 0: # Range Plot
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotSingleTargetRangeQT(self.simulationHandler.getScenarioData(), self.selectedTarget)
                self.plotWidget.canvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel)

            if self.figureSelectionDropDown.currentIndex() == 1: # Range Rate Plot
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotSingleTargetRangeRateQT(self.simulationHandler.getScenarioData(), self.selectedTarget)
                self.plotWidget.canvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel, dashedData = [2,3])

            if self.figureSelectionDropDown.currentIndex() == 2: # Az/El Plot
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotSingleTargetAzElQT(self.simulationHandler.getScenarioData(), self.selectedTarget)
                self.plotWidget.canvas.update_multi_figure(labels, arraysToPlot, title, xLabel, yLabel, False)

class DetectionTab(QWidget):
    def __init__(self, parent, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.simulationHandler = simulationHandler

        self.detectionTableLabel = QLabel("Detections")

        self.detectionTable = QTableWidget()
        self.detectionTable.setColumnCount(5)
        self.detectionTable.setRowCount(20)
        self.detectionTable.cellClicked.connect(self.updateFigure)

        self.updateDetListButton = QPushButton("Update Detection List")
        self.updateDetListButton.clicked.connect(self.updateDetectionList)

        self.figureSelectionLabel = QLabel("Figure Type")
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Ambiguous R/D Matrix", "Unfolded R/D Matrix"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.notchEchoesTableLabel = QLabel("MBC Notch Echoes")
        
        self.notchEchoesTable = QTableWidget()
        self.notchEchoesTable.setColumnCount(5)
        self.notchEchoesTable.setRowCount(20)

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.plotWidget = FigureWidget()

        self.layout1.addWidget(self.detectionTableLabel)
        self.layout1.addWidget(self.detectionTable)
        self.layout1.addWidget(self.updateDetListButton)
        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        self.layout1.addWidget(self.notchEchoesTableLabel)
        self.layout1.addWidget(self.notchEchoesTable)
               
        #self.layout1.addStretch()

        self.layout2.addWidget(self.plotWidget)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)

    def updateDetectionList(self):
        if self.simulationHandler.getSimulationPerformed():
            detections = self.simulationHandler.getSimResults()["DetectionReports"]
            detectionsHeader = self.simulationHandler.getSimResults()["DetectionReportsHeader"]

            self.detectionTable.setColumnCount(len(detections[0]))
            self.detectionTable.setRowCount(len(detections)+1)

            for col in range(len(detectionsHeader)):
                self.detectionTable.setItem(0, col, QTableWidgetItem(detectionsHeader[col]))

            for row in range(1, len(detections)+1):
                for col in range(len(detections[0])):
                    self.detectionTable.setItem(row, col, QTableWidgetItem(str(round(detections[row-1][col], 3))))

            header = self.detectionTable.horizontalHeader()       
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for col in range(1, len(detections[0])):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

            filteredEchoes = self.simulationHandler.getSimResults()["FilteredEchoes"]
            filteredEchoesHeader = self.simulationHandler.getSimResults()["FilteredEchoesHeader"]

            if (len(filteredEchoes) > 0):
                self.notchEchoesTable.setColumnCount(len(filteredEchoes[0]))
                self.notchEchoesTable.setRowCount(len(filteredEchoes)+1)

                for col in range(len(filteredEchoesHeader)):
                    self.notchEchoesTable.setItem(0, col, QTableWidgetItem(filteredEchoesHeader[col]))

                for row in range(1, len(filteredEchoes)+1):
                    for col in range(len(filteredEchoes[0])):
                        self.notchEchoesTable.setItem(row, col, QTableWidgetItem(str(round(filteredEchoes[row-1][col], 3))))

            

    def updateFigure(self):
        if self.simulationHandler.getSimulationPerformed():

            visualizer = self.simulationHandler.getVisualizer()

            if self.figureSelectionDropDown.currentIndex() == 0:
                if self.detectionTable.currentRow() > 0:
                    detNo = self.detectionTable.currentRow()
                else:
                    detNo = 1
                labels, points, lines, title, xLabel, yLabel = visualizer.plotAmbiguousRangeDopplerMatrixOfDetectionQT(self.simulationHandler.getSimResults(), detNo)
                self.plotWidget.canvas.update_point_figure_2dim(labels, points, [], lines, title, xLabel, yLabel)

            if self.figureSelectionDropDown.currentIndex() == 1:
                if self.detectionTable.currentRow() > 0:
                    detNo = self.detectionTable.currentRow()
                else:
                    detNo = 1
                labels, points, title, xLabel, yLabel, ticks = visualizer.plotRangeUnfoldOfEchoesOfDetectionQT(self.simulationHandler.getSimResults(), detNo)
                self.plotWidget.canvas.update_point_figure_2dim(labels, points, [], [], title, xLabel, yLabel, ticks=ticks)

class DetectionPictureTab(QWidget):
    def __init__(self, parent, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.simulationHandler = simulationHandler

        self.figureTypeTableLabel = QLabel("Figure Type")

        
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Detections vs N/E"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.plotWidget = FigureWidget()

        self.layout1.addWidget(self.figureTypeTableLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
                       
        self.layout1.addStretch()

        self.layout2.addWidget(self.plotWidget)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,2)
        self.columnsLayout.setColumnStretch(2,8)

    def updateFigure(self):
         if self.simulationHandler.getSimulationPerformed():

            visualizer = self.simulationHandler.getVisualizer()

            detections = self.simulationHandler.getSimResults()["DetectionReports"]
            ownshipNEDatDetection = self.simulationHandler.getSimResults()["OwnshipNEDatDetection"]

            if self.figureSelectionDropDown.currentIndex() == 0: # N/E Plot
                labels, points, lines, title, xLabel, yLabel= visualizer.plotTargetScenarioTopDownAndDetectionReportsQT(self.simulationHandler.getScenarioData(), detections, ownshipNEDatDetection)
                self.plotWidget.canvas.update_point_figure_2dim([], points, labels, lines, title, xLabel, yLabel, aspectForced=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())