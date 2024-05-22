
from OutputStore import OutputStore
from Ownship import Ownship
from RadarVisualizer import RadarVisualizer
from RfEnvironment import RfEnvironment
from Processor.ScenarioProcessor import ScenarioProcessor
from Radar import Radar
from RadarReplay import RadarReplay
import tkinter as tk
import time

# TODO: Tidy Up the directory

class RadarSimulator:
    
    def __init__(self) -> None:
        self.scenarioProcessor = ScenarioProcessor()
        self.outputStore = OutputStore()
        
        self.windowHandlerList = []

        self.startGUI()

    def startGUI(self):

        self.window = tk.Tk()
        self.window.wm_title("Radar Tracker Testbed")

        frmCol1 = tk.Frame(pady=10, padx=10)

        lblRadarFile = tk.Label(master=frmCol1, text="Radar File:")
        lblRadarFile.grid(row = 1, column = 1)

        lblRadarSettingsFile = tk.Label(master=frmCol1, text="Radar Settings File:")
        lblRadarSettingsFile.grid(row=2, column=1)

        lblScenarioFile = tk.Label(master=frmCol1, text="Scenario File:")
        lblScenarioFile.grid(row=3, column=1)

        lblSimulationFile = tk.Label(master=frmCol1, text="Simulation File:")
        lblSimulationFile.grid(row=4, column=1)

        self.entRadarFile = tk.Entry(master=frmCol1, )
        self.entRadarFile.insert(0, "radar.json")
        self.entRadarFile.grid(row=1, column = 2)

        self.entRadarSettingsFile = tk.Entry(master=frmCol1, )
        self.entRadarSettingsFile.insert(0, "radar_setting.json")
        self.entRadarSettingsFile.grid(row=2, column = 2)

        self.entScenarioFile = tk.Entry(master=frmCol1, )
        self.entScenarioFile.insert(0, "scenario_notching_2ship.json")
        self.entScenarioFile.grid(row=3, column = 2)

        self.entSimulationFile = tk.Entry(master=frmCol1, )
        self.entSimulationFile.insert(0, "sim.json")
        self.entSimulationFile.grid(row=4, column = 2)

        self.btnLoadScenario = tk.Button(master=frmCol1, text = "Load Scenario", width=30)
        self.btnLoadScenario.grid(row=5, column = 1, columnspan=2)
        self.btnLoadScenario.bind("<Button-1>", self.loadScenario)

        self.btnStartRadarSimulation = tk.Button(master=frmCol1, text = "Start Simulation", width = 30, state="disabled")
        self.btnStartRadarSimulation.grid(row=6, column=1, columnspan=2)
        self.btnStartRadarSimulation.bind("<Button-1>", self.startRadarSimulation)

        frmCol1.grid(row=1, column=1, sticky="N")

        frmCol2 = tk.Frame(pady=10, padx=10)

        self.btnDrawAntennaMovement = tk.Button(master = frmCol2, text="Draw Antenna Movement", width=20, state="disabled")
        self.btnDrawAntennaMovement.grid(row = 1, column = 1)
        self.btnDrawAntennaMovement.bind("<Button-1>", self.drawAntennaMovement)

        self.btnDrawClutterVelocities = tk.Button(master = frmCol2, text="Draw Clutter Velocities", width=20, state="disabled")
        self.btnDrawClutterVelocities.grid(row = 2, column = 1)
        self.btnDrawClutterVelocities.bind("<Button-1>", self.drawClutterVelocities)

        self.btnDrawEchoRanges = tk.Button(master = frmCol2, text="Draw Amb. Echo Ranges", width=20, state="disabled")
        self.btnDrawEchoRanges.grid(row = 3, column = 1)
        self.btnDrawEchoRanges.bind("<Button-1>", self.drawEchoRanges)

        self.btnDrawDetectionRanges = tk.Button(master = frmCol2, text="Draw Det. Report Ranges", width=20, state="disabled")
        self.btnDrawDetectionRanges.grid(row = 4, column = 1)
        self.btnDrawDetectionRanges.bind("<Button-1>", self.drawDetectionRanges)

        # TODO: Rework all Bindings to Commands!
        self.btnDrawDetectionRangeRates = tk.Button(master = frmCol2, text="Draw Det. Report Range Rates", width=20, state="disabled", command=self.drawDetectionRangeRates)
        self.btnDrawDetectionRangeRates.grid(row = 5, column = 1)

        self.btnDrawDetectionNE = tk.Button(master=frmCol2, text="Draw Det. Report North East", width=20, state="disabled", command=self.drawDetectionNorthEast)
        self.btnDrawDetectionNE.grid(row=6, column = 1)

        frmCol2.grid(row=1, column=2, sticky="N")

        frmCol3 = tk.Frame(pady = 10, padx = 10)

        lblTargetSelect = tk.Label(master=frmCol3, text="Target select:")
        lblTargetSelect.grid(row = 1, column = 1)

        self.entTargetSelect = tk.Entry(master = frmCol3, width=5)
        self.entTargetSelect.insert(0, "1")
        self.entTargetSelect.grid(row = 1, column = 2)

        self.btnDrawSingleTgtRange = tk.Button(master=frmCol3, text="Draw Single Target Range", width=20, state="disabled")
        self.btnDrawSingleTgtRange.grid(row = 2, column = 1, columnspan = 2)
        self.btnDrawSingleTgtRange.bind("<Button-1>", self.drawSingleTgtRange)

        lblDetectionSelect = tk.Label(master=frmCol3, text="Detection select:")
        lblDetectionSelect.grid(row = 3, column = 1)

        self.entDetectionSelect = tk.Entry(master = frmCol3, width=5)
        self.entDetectionSelect.insert(0, "1")
        self.entDetectionSelect.grid(row = 3, column = 2)

        self.btnDrawAmbR_D_Mat = tk.Button(master=frmCol3, text="Draw Amb. R/D Mat.", width=20, state="disabled", command=self.drawAmbRDMat)
        self.btnDrawAmbR_D_Mat.grid(row = 4, column = 1, columnspan = 2)

        self.btnDrawRangeUnfoldR_D_Mat = tk.Button(master=frmCol3, text="Draw Range Unfold R/D Mat.", width=20, state="disabled", command=self.drawRangeUnfoldRDMat)
        self.btnDrawRangeUnfoldR_D_Mat.grid(row = 5, column = 1, columnspan = 2)

        frmCol3.grid(row = 1, column = 3, sticky = "N")

        frmCol4 = tk.Frame(pady = 10, padx = 10)

        self.btnDrawScenario = tk.Button(master = frmCol4, text="Draw Scenario", width=20, state="disabled")
        self.btnDrawScenario.grid(row = 1, column = 1)
        self.btnDrawScenario.bind("<Button-1>", self.drawScenario)

        self.btnDrawTgtScenario = tk.Button(master = frmCol4, text="Draw Target Scenario", width=20, state="disabled")
        self.btnDrawTgtScenario.grid(row = 2, column = 1)
        self.btnDrawTgtScenario.bind("<Button-1>", self.drawTgtScenario)

        frmCol4.grid(row = 1, column = 4, sticky = "N")

        self.statusText = tk.Text(height=15)
        self.statusText.grid(row=2, column=1, columnspan=2)

        frmColB3 = tk.Frame(pady = 10, padx = 10)

        self.btnDrawEclipsingRanges = tk.Button(master = frmColB3, text="Draw Eclipsing Ranges", width=20, state="disabled")
        self.btnDrawEclipsingRanges.grid(row = 1, column = 1)
        self.btnDrawEclipsingRanges.bind("<Button-1>", self.drawRangeEclipsingZones)

        frmColB3.grid(row = 2, column = 3, sticky = "N")

        frmColB4 = tk.Frame(pady=10, padx=10)

        self.btnStartReplay = tk.Button(master = frmColB4, text="Start Replay", width=20, state="disabled", command=self.startReplay)
        self.btnStartReplay.grid(row = 1, column = 1)

        frmColB4.grid(row = 2, column = 4, sticky = "N")

        self.window.mainloop()

    # Button Methods

    def loadScenario(self, event):
        scenarioFile = "Scenarios/" + self.entScenarioFile.get()
        radarFile = self.entRadarFile.get()
        
        self.scenario = self.scenarioProcessor.processJsonScenario(scenarioFile, radarFile)

        self.rfEnvironment = RfEnvironment(self.scenario, self.entSimulationFile.get(), self.entRadarFile.get())
        self.ownship = Ownship(self.scenario, self.entRadarFile.get())
        
        self.radar = Radar(self.entRadarFile.get(), self.entRadarSettingsFile.get(), self.rfEnvironment, self.ownship)

        self.visualizer = RadarVisualizer(self.entRadarFile.get(), self.entSimulationFile.get())

        self.provideScenarioStatusText()

        self.btnDrawScenario["state"] = "normal"
        self.btnDrawTgtScenario["state"] = "normal"
        self.btnStartRadarSimulation["state"] = "normal"
        self.btnDrawSingleTgtRange["state"] = "normal"
        self.btnDrawEclipsingRanges["state"] = "normal"

        self.btnLoadScenario["state"] = "disabled"

        print("Scenario Loaded")

    def startRadarSimulation(self, event):
        
        if self.btnStartRadarSimulation["state"] != "disabled":
            print("Sim started")
            maxOwnshipTime = self.scenario[0][-1][0]
            print("Simulating " + str(maxOwnshipTime) + "s...")
            startTime = time.time()
            self.simResult = self.radar.operate(maxOwnshipTime)
            endTime = time.time()
            duration = endTime - startTime

            self.provideSimulationStatusText(duration)

            self.outputStore.writeSimResultToDisk(self.simResult)        

            self.btnDrawAntennaMovement["state"] = "normal"
            self.btnDrawEchoRanges["state"] = "normal"
            self.btnDrawDetectionRanges["state"] = "normal"
            self.btnDrawDetectionRangeRates["state"] = "normal"
            self.btnDrawDetectionNE["state"] = "normal"
            self.btnDrawClutterVelocities["state"] = "normal"
            self.btnDrawAmbR_D_Mat["state"] = "normal"
            self.btnDrawRangeUnfoldR_D_Mat["state"] = "normal"
            self.btnStartReplay["state"] = "normal"

            self.btnStartRadarSimulation["state"] = "disabled"

    def drawScenario(self, event):
        if self.btnDrawScenario["state"] != "disabled":
            self.visualizer.plotCompleteScenarioTopDown(self.scenario)

    def drawTgtScenario(self, event):
        if self.btnDrawTgtScenario["state"] != "disabled":
            self.visualizer.plotTargetScenarioTopDown(self.scenario)

    def drawAntennaMovement(self, event):
        
        if self.btnDrawAntennaMovement["state"] != "disabled":
            self.window.update()
            #thread = Thread(target=self.visualizer.plotAntennaMovement, args=[self.simResult["AntennaAngles"]])
            #thread.start()

            self.visualizer.plotAntennaMovement(self.simResult["AntennaAngles"])

    def drawEchoRanges(self, event):
        if self.btnDrawEchoRanges["state"] != "disabled":
            self.visualizer.plotEchoRanges(self.simResult["Echoes"])

    def drawDetectionRanges(self, event):
        if self.btnDrawEchoRanges["state"] != "disabled":
            self.visualizer.plotAllTargetRangesAndDetectionReports(self.scenario, self.simResult["DetectionReports"])

    def drawDetectionRangeRates(self):
        if self.btnDrawDetectionRangeRates["state"] != "disabled":
            self.visualizer.plotAllTargetRangeRatesAndDetectionReports(self.scenario, self.simResult["DetectionReports"])

    def drawDetectionNorthEast(self):
        if self.btnDrawDetectionNE["state"] != "disabled":
            newWin = tk.Toplevel(self.window)
            self.visualizer.plotTargetScenarioTopDownAndDetectionReports(self.scenario, self.simResult["DetectionReports"], self.simResult["OwnshipNEDatDetection"], newWin)

    def drawAmbRDMat(self):
        if self.btnDrawAmbR_D_Mat["state"] != "disabled":
            newWin = tk.Toplevel(self.window)
            self.visualizer.plotAmbiguousRangeDopplerMatrixOfDetection(self.simResult, int(self.entDetectionSelect.get()), newWin)

    def drawRangeUnfoldRDMat(self):
        if self.btnDrawRangeUnfoldR_D_Mat["state"] != "disabled":
            newWin = tk.Toplevel(self.window)
            self.visualizer.plotRangeUnfoldOfEchoesOfDetection(self.simResult, int(self.entDetectionSelect.get()), newWin)

    def drawSingleTgtRange(self, event):
        if self.btnDrawSingleTgtRange["state"] != "disabled":
            self.visualizer.plotSingleTargetRange(self.scenario, int(self.entTargetSelect.get()))

    def drawRangeEclipsingZones(self, event):
        if self.btnDrawEclipsingRanges["state"] != "disabled":
            self.visualizer.plotEclipsingZones()

    def drawClutterVelocities(self, event):
        if self.btnDrawClutterVelocities["state"] != "disabled":
            newWin = tk.Toplevel(self.window)
            self.visualizer.plotClutterVelocities(self.simResult["ClutterVelocities"], newWin)

    def startReplay(self):
        if self.btnStartReplay["state"] != "disabled":
            replay = RadarReplay("replay.json", self.entRadarFile.get(), self.entRadarSettingsFile.get(), self.simResult)

    # Text Outputs
    def provideSimulationStatusText(self, simtime):
        
        self.statusText.insert(tk.END, "Simulation duration: " + str(simtime) + " s\n")
        self.statusText.insert(tk.END, "Scan Bars with Detections: " + str(self.simResult["BarsWithDetections"]) + "\n")
        self.statusText.insert(tk.END, "Detections: 1.." + str(len(self.simResult["DetectionReports"])) + "\n")
        # TODO: log number of bursts required per detection

    def provideScenarioStatusText(self):
        osStart = self.scenario[0][0][0]
        osEnd = self.scenario[0][-1][0]
        self.statusText.insert(tk.END, "Ownship data Times: " + str([osStart, osEnd]) + "\n")
        
        targetNo = 1
        for target in range (1, len(self.scenario)):
            self.statusText.insert(tk.END, "Target " + str(targetNo) + " Times: " + str([self.scenario[target][0][0], self.scenario[target][-1][0]]) + "\n")
            targetNo += 1

if __name__ == "__main__":
    rs = RadarSimulator()
   
    
