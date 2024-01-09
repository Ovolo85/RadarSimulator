import sys, os, time, math
import numpy as np
from sys import platform
import subprocess
from functools import partial



# Qt
from PyQt5.QtWidgets import QSizePolicy, QComboBox, QPlainTextEdit, QGridLayout, QLineEdit, QMainWindow, QApplication, QPushButton, QWidget, QTabWidget,QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon

# MatplotLib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# Own Modules
from ScenarioProcessor import ScenarioProcessor
from Ownship import Ownship
from RadarVisualizer import RadarVisualizer
from RfEnvironment import RfEnvironment
from Radar import Radar
from OutputStore import OutputStore


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
        self.width = 1200    
        self.height = 600
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
        self.scenarioFile = ""

    def setSimFiles(self, radar, radarsettings, sim):
        self.radarFile = radar
        self.radarSettingsFile = radarsettings
        self.simSettingsFile = sim
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
        
    def getRadarFile(self):
        return self.radarFile
    
    def getRadarSettingsFile(self):
        return self.radarSettingsFile
    
    def getSimSettingsFile(self):
        return self.simSettingsFile
    
    def getScenarioFile(self):
        return self.scenarioFile
        
    def getDataLoaded(self):
        return self.dataLoaded

class SimulationHandler():
    def __init__(self, dataStore : DataStore, outputStore : OutputStore) -> None:
        self.dataStore = dataStore
        self.outputStore = outputStore
        
        self.scenarioProcessor = ScenarioProcessor()

        self.simulationPerformed = False

    def startSimulation(self, output : QPlainTextEdit):
        
        self.scenario = self.scenarioProcessor.processScenario(self.dataStore.getScenarioFile(), self.dataStore.getRadarFile())
        output.insertPlainText("Scenario " + self.dataStore.getScenarioFile() + " processed...\n")
        self.outputAircraftTimesFromScenario(output)

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

        self.dataStore.setSimFiles(radar, radarsettings, simsettings)

        self.outputText.setPlainText("")

        self.outputText.insertPlainText("RADAR: " + radar + "\n")
        self.outputText.insertPlainText(self.dataStore.readRadarFileAsText() + "\n")
        
        self.outputText.insertPlainText("RADAR SETTINGS: " + radarsettings + "\n")
        self.outputText.insertPlainText(self.dataStore.readRadarSettingsFileAsText() + "\n")

        self.outputText.insertPlainText("SIM SETTINGS: " + simsettings + "\n")
        self.outputText.insertPlainText(self.dataStore.readSimSettingsFileAsText() + "\n")
    
    def editFile(self, file):
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
        self.figureSelectionDropDown.addItems(["Target Scenario N/E", "Complete Scenario N/E"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.plotCanvas = StaticFigureCanvas()

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

        self.layout2.addWidget(self.plotCanvas)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)

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
                self.plotCanvas.update_figure_2dim(labels, arraysToPlot, title, xLabel, yLabel, True)
            if self.figureSelectionDropDown.currentIndex() == 1:
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotCompleteScenarioTopDownQT(self.simulationHandler.getScenarioData())
                self.plotCanvas.update_figure_2dim(labels, arraysToPlot, title, xLabel, yLabel, True)
        else:
            self.plotCanvas.clear_figure()
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
        subprocess.run(['open', file], check=True)
        
        #if platform == "darwin":
        #    subprocess.call(('open', file))
        #elif platform == "win32":
        #    os.startfile(file)

class PureRadarDataTab(QWidget):
    def __init__(self, parent, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.simulationHandler = simulationHandler

        self.figureSelectionLabel = QLabel("Figure Type")
        self.figureSelectionDropDown = QComboBox()
        self.figureSelectionDropDown.addItems(["Eclipsing Zones", "Antenna Angles", "Clutter Velocities"])
        self.figureSelectionDropDown.activated.connect(self.updateFigure)

        self.statusOutput = QPlainTextEdit()
        self.statusOutput.setReadOnly(True)

        self.plotCanvas = StaticFigureCanvas()

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        self.layout1.addWidget(self.statusOutput)

        self.layout1.addStretch()

        self.layout2.addWidget(self.plotCanvas)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)

    def updateFigure(self):
        if self.simulationHandler.getSimulationPerformed():
            if self.figureSelectionDropDown.currentIndex() == 0:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arrayOfArrays, title, xLabels, yLabels = visualizer.plotEclipsingZonesQT()
                self.plotCanvas.update_multi_figure(labels, arrayOfArrays, title, xLabels, yLabels, labelsOff=True)
            if self.figureSelectionDropDown.currentIndex() == 1:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arrayOfArrays, title, xLabels, yLabels = visualizer.plotAntennaMovementQT(self.simulationHandler.getSimResults()["AntennaAngles"])
                self.plotCanvas.update_multi_figure(labels, arrayOfArrays, title, xLabels, yLabels, labelsOff=False)
            if self.figureSelectionDropDown.currentIndex() == 2:
                visualizer = self.simulationHandler.getVisualizer()
                labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotClutterVelocitiesQT(self.simulationHandler.getSimResults()["ClutterVelocities"])
                self.plotCanvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel)
            
        else:
            self.plotCanvas.clear_figure()
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
        self.figureSelectionDropDown.addItems(["Range to Target"])
        
        self.plotCanvas = StaticFigureCanvas()

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()

        self.layout1.addLayout(self.targetSelectBoxLayout)
        self.layout1.addWidget(self.setTargetButton)
        self.layout1.addWidget(self.figureSelectionLabel)
        self.layout1.addWidget(self.figureSelectionDropDown)
        
        self.layout1.addStretch()

        self.layout2.addWidget(self.plotCanvas)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)          
            
    def setTarget(self):
        if self.simulationHandler.getSimulationPerformed() & self.targetSelectEntry.text().isnumeric():
                tgtNo = int(self.targetSelectEntry.text())
                if tgtNo > 0 & tgtNo <= self.simulationHandler.getNumberOfTargets():
                    self.selectedTarget = int(self.targetSelectEntry.text())
                    self.updateFigure()

    def updateFigure(self):
        visualizer = self.simulationHandler.getVisualizer()
        labels, arraysToPlot, title, xLabel, yLabel = visualizer.plotSingleTargetRangeQT(self.simulationHandler.getScenarioData(), self.selectedTarget)
        self.plotCanvas.update_figure_1dim(labels, arraysToPlot, title, xLabel, yLabel)



class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.fig = Figure(tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        self.axes.plot()
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class StaticFigureCanvas(FigureCanvas):
    def update_figure_2dim(self, labels, arraysToPlot, title, xLabel, yLabel, aspectForced):
        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        for i in range(len(arraysToPlot)):
            arrayToPlot = arraysToPlot[i]
            self.axes.plot(arrayToPlot[:,2], arrayToPlot[:,1], label=labels[i])
        
        self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)
        if aspectForced:
            self.axes.set_aspect(1)
            xWidth = abs(self.axes.get_xlim()[0] - self.axes.get_xlim()[1])
            yWidth = abs(self.axes.get_ylim()[0] - self.axes.get_ylim()[1])
            xyWidthDiff = abs(xWidth-yWidth)
            if yWidth > 0.75 * xWidth:
                xAddition = xyWidthDiff/0.75 / 2
                self.axes.set_xlim([self.axes.get_xlim()[0] - xAddition, self.axes.get_xlim()[1] + xAddition])
            else: 
                pass
        else:
            self.axes.set_aspect("auto")
        
        self.axes.grid(True)

        self.draw()

    def update_figure_1dim(self, labels, arraysToPlot, title, xLabel, yLabel):
        self.axes.cla()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        for i in range(len(arraysToPlot)):
            arrayToPlot = arraysToPlot[i]
            self.axes.plot(arrayToPlot[:,0], arrayToPlot[:,1], label=labels[i])
        
        self.axes.legend(loc="upper right")
        self.axes.set_title(title)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)

        self.axes.grid(True)

        self.draw()

    def update_multi_figure(self, labels, arraysToPlot, title, xLabel, yLabel, labelsOff):
        self.axes.cla()
        self.fig.clf()


        for i in range(len(labels)):
            ax = self.fig.add_subplot(len(arraysToPlot), 1, i+1)
            ax.plot(arraysToPlot[i][:,0], arraysToPlot[i][:,1])
            if i == 0: 
                ax.set_title(title)
            if not labelsOff:
                ax.set_xlabel(xLabel[i])
                ax.set_ylabel(yLabel[i])

        #self.axes.grid(True)

        self.draw()


    def clear_figure(self):
        self.axes.cla()
        self.fig.clf()

        self.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())