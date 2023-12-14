import sys, os, time
import numpy as np

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

class MyTableWidget(QWidget):
    
    def __init__(self, parent, dataStore, simulationHandler):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
                
        # Add tabs
        self.tabs.addTab(SetupTab(self, dataStore), "Setup")
        self.tabs.addTab(ScenarioTab(self, dataStore, simulationHandler), "Scenario")
                
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

        self.radarSettingsFileLabel = QLabel("Radar Settings File")
        self.radarSettingsFileName = QLineEdit()
        self.radarSettingsFileName.setText("radar_setting.json")

        self.simulationSettingsFileLabel = QLabel("Simulation Settings File")
        self.simulationSettingsFileName = QLineEdit()
        self.simulationSettingsFileName.setText("sim.json")

        self.loadConfigButton = QPushButton("Load Configuration")
        self.loadConfigButton.clicked.connect(self.loadConfiguration)

        self.outputText = QPlainTextEdit()
        self.outputText.setReadOnly(True)
        
        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout(self)
        self.layout2 = QVBoxLayout(self)
        
        self.layout1.addWidget(self.radarConfigFileLabel)
        self.layout1.addWidget(self.radarConfigFileName)
        self.layout1.addWidget(self.radarSettingsFileLabel)
        self.layout1.addWidget(self.radarSettingsFileName)
        self.layout1.addWidget(self.simulationSettingsFileLabel)
        self.layout1.addWidget(self.simulationSettingsFileName)
        self.layout1.addWidget(self.loadConfigButton)
        self.layout1.addStretch()

        self.layout2.addWidget(self.outputText)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)
        self.setLayout(self.columnsLayout)

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
        
class ScenarioTab(QWidget):
    def __init__(self, parent, datastore : DataStore, simulationHandler : SimulationHandler):
        super(QWidget, self).__init__(parent)

        self.dataStore = datastore
        self.simulationHandler = simulationHandler
        
        self.scenarioFileLabel = QLabel("Scenario File")
        self.scenarioDropDown = QComboBox()
        self.updateScenarioFilesFromFolder()
        self.updateFolderButton = QPushButton("Update Folder Content")
        self.updateFolderButton.clicked.connect(self.updateScenarioFilesFromFolder)
        self.startProcessingButton = QPushButton("Start Simulation")
        self.startProcessingButton.clicked.connect(self.startSimulation)
        self.statusOutput = QPlainTextEdit()

        self.plotCanvas = StaticFigureCanvas()
        #self.plotCanvas.update_figure(5)

        self.columnsLayout = QGridLayout(self)
        self.layout1 = QVBoxLayout(self)
        self.layout2 = QVBoxLayout(self)

        self.layout1.addWidget(self.scenarioFileLabel)
        self.layout1.addWidget(self.scenarioDropDown)
        self.layout1.addWidget(self.updateFolderButton)
        self.layout1.addWidget(self.startProcessingButton)
        self.layout1.addWidget(self.statusOutput)
        self.layout1.addStretch()

        self.layout2.addWidget(self.plotCanvas)

        self.columnsLayout.addLayout(self.layout1, 1, 1)
        self.columnsLayout.addLayout(self.layout2, 1, 2)
        self.columnsLayout.setColumnStretch(1,3)
        self.columnsLayout.setColumnStretch(2,7)
        self.setLayout(self.columnsLayout)

    def updateScenarioFilesFromFolder(self):
        scenariolist =  os.listdir("Scenarios")
        self.scenarioDropDown.clear()
        for s in scenariolist:
            self.scenarioDropDown.addItem(s)

    def startSimulation(self):
        self.statusOutput.setPlainText("")
        if self.dataStore.getDataLoaded() == False:
            self.statusOutput.insertPlainText("ERROR: Please load the Config Files in the Setup Tab first!")
        else: 
            self.dataStore.setScenarioFile("Scenarios/" + self.scenarioDropDown.currentText())
            self.simulationHandler.startSimulation(self.statusOutput)
            self.provideScenarioStatusText()
        
    def provideScenarioStatusText(self):
        pass   

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        fig = Figure(figsize=(10,7))
        self.axes = fig.add_subplot(111)
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)
        self.axes.plot()
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class StaticFigureCanvas(FigureCanvas):
    def update_figure(self, f):
        self.axes.cla()
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(f*np.pi*t)
        self.axes.plot(t, s)
        self.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())