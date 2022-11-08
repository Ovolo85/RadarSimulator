from RadarVisualizer import RadarVisualizer
from RfEnvironment import RfEnvironment
from ScenarioProcessor import ScenarioProcessor
from Radar import Radar
import tkinter as tk
import time

class RadarSimulator:
    # Git Test Comment
    def __init__(self) -> None:
        self.scenarioProcessor = ScenarioProcessor()
        
        
        self.startGUI()

    def startGUI(self):

        window = tk.Tk()

        frmInputFiles = tk.Frame(borderwidth=20)

        lblRadarFile = tk.Label(master=frmInputFiles, text="Radar File:")
        lblRadarFile.grid(row = 1, column = 1)

        lblRadarSettingsFile = tk.Label(master=frmInputFiles, text="Radar Settings File:")
        lblRadarSettingsFile.grid(row=2, column=1)

        lblScenarioFile = tk.Label(master=frmInputFiles, text="Scenario File:")
        lblScenarioFile.grid(row=3, column=1)

        self.entRadarFile = tk.Entry(master=frmInputFiles, )
        self.entRadarFile.insert(0, "radar.json")
        self.entRadarFile.grid(row=1, column = 2)

        self.entRadarSettingsFile = tk.Entry(master=frmInputFiles, )
        self.entRadarSettingsFile.insert(0, "radar_setting.json")
        self.entRadarSettingsFile.grid(row=2, column = 2)

        self.entScenarioFile = tk.Entry(master=frmInputFiles, )
        self.entScenarioFile.insert(0, "scenario.json")
        self.entScenarioFile.grid(row=3, column = 2)

        frmInputFiles.grid(row=1, column=1, rowspan=5)

        frmStartSimulationButtons = tk.Frame(borderwidth=20)

        self.btnLoadScenario = tk.Button(master=frmStartSimulationButtons, text = "Load Scenario", width=30)
        self.btnLoadScenario.grid(row=1, column = 1)
        self.btnLoadScenario.bind("<Button-1>", self.loadScenario)

        self.btnStartRadarSimulation = tk.Button(master=frmStartSimulationButtons, text = "Start Simulation", width = 30, state="disabled")
        self.btnStartRadarSimulation.grid(row=2, column=1)
        self.btnStartRadarSimulation.bind("<Button-1>", self.startRadarSimulation)

        frmStartSimulationButtons.grid(row=6, column=1)

        self.btnDrawScenario = tk.Button(text="Draw Scenario", width=30, state="disabled")
        self.btnDrawScenario.grid(row = 1, column = 2, pady=5)
        self.btnDrawScenario.bind("<Button-1>", self.drawScenario)

        self.btnDrawTgtScenario = tk.Button(text="Draw Target Scenario", width=30, state="disabled")
        self.btnDrawTgtScenario.grid(row = 2, column = 2, pady=5)
        self.btnDrawTgtScenario.bind("<Button-1>", self.drawTgtScenario)

        self.btnDrawAntennaMovement = tk.Button(text="Draw Antenna Movement", width=30, state="disabled")
        self.btnDrawAntennaMovement.grid(row = 3, column = 2, pady=5)
        self.btnDrawAntennaMovement.bind("<Button-1>", self.drawAntennaMovement)

        self.btnDrawEchoRanges = tk.Button(text="Draw Amb. Echo Ranges", width=30, state="disabled")
        self.btnDrawEchoRanges.grid(row = 4, column = 2, pady=5)
        self.btnDrawEchoRanges.bind("<Button-1>", self.drawEchoRanges)

        window.mainloop()

    def loadScenario(self, event):
        scenarioFile = self.entScenarioFile.get()
        radarFile = self.entRadarFile.get()
        
        self.scenario = self.scenarioProcessor.processScenario(scenarioFile, radarFile)

        # TODO: sim.json is still hardcoded. UI Entry?
        self.rfEnvironment = RfEnvironment(self.scenario, "sim.json", self.entRadarFile.get())
        
        self.radar = Radar(self.entRadarFile.get(), self.entRadarSettingsFile.get(), self.rfEnvironment)

        self.visualizer = RadarVisualizer(self.entRadarFile.get())

        self.btnDrawScenario["state"] = "normal"
        self.btnDrawTgtScenario["state"] = "normal"
        self.btnStartRadarSimulation["state"] = "normal"

        self.btnLoadScenario["state"] = "disabled"

    def startRadarSimulation(self, event):
        maxOwnshipTime = self.scenario[0][-1][0]
        print("Simulating " + str(maxOwnshipTime) + "s...")
        startTime = time.time()
        self.simResult = self.radar.operate(maxOwnshipTime)
        endTime = time.time()

        print("Simulation duration: " + str(endTime - startTime) + " s")

        self.btnDrawAntennaMovement["state"] = "normal"
        self.btnDrawEchoRanges["state"] = "normal"

    def drawScenario(self, event):
        if self.btnDrawScenario["state"] != "disabled":
            self.visualizer.plotCompleteScenarioTopDown(self.scenario)

    def drawTgtScenario(self, event):
        if self.btnDrawTgtScenario["state"] != "disabled":
            self.visualizer.plotTargetScenarioTopDown(self.scenario)

    def drawAntennaMovement(self, event):
        if self.btnDrawAntennaMovement["state"] != "disabled":
            self.visualizer.plotAntennaMovement(self.simResult["AntennaAngles"])

    def drawEchoRanges(self, event):
        if self.btnDrawEchoRanges["state"] != "disabled":
            self.visualizer.plotEchoRanges(self.simResult["Echoes"])

if __name__ == "__main__":
    rs = RadarSimulator()
   
    
