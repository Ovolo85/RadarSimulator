import json


class RfEnvironment:
    
    def __init__(self, scenario, simulationSettingFile, radarFile) -> None:
        self.scenario = scenario
        self.getSimulationSettingFromJSON(simulationSettingFile)
        self.getRadarDataFromJSON(radarFile)

    def measure(self, prf, pw, az, el, time):
        targetPositionsAtTime = []
        for target in range(len(self.scenario)-1):
            for targetPosition in self.scenario[target+1]:
                if abs(targetPosition[0] - time) < self.BurstLength / 100:
                    targetPositionsAtTime.append(targetPosition)
                    break

        pass
        
        #print([prf, pw, az, el])

    def getSimulationSettingFromJSON(self, simulationSettingFile):
        with open(simulationSettingFile) as json_file:
            data = json.load(json_file)
        self.measuremenNoise = data["MeasurementNoise"]
        self.eclipsingEnabled = data["RangeEclipsing"]

    def getRadarDataFromJSON(self, radarFile):
        with open(radarFile) as json_file:
            data = json.load(json_file)
        self.BurstLength = data["BurstLength"]