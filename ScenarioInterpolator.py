import csv

class ScenarioInterpolator:
    
    def __init__(self, burstRate):
        self.burstRate = burstRate

    def interpolateScenario(self, scenario):
        pass

    def interpolateScenarioFile(self, scenarioFiles):
        scenario = []
        single_aircraft_scenario = []
        
        for file in scenarioFiles:
            with open(file, "r") as f:
                reader = csv.reader(f, delimiter=",")
                next(reader) # skip first line
                for row in reader:
                    single_aircraft_scenario.append(row)
            scenario.append(single_aircraft_scenario)
            single_aircraft_scenario = []

        return scenario
    
if __name__ == "__main__":
    si = ScenarioInterpolator(0.005)
    sc = si.interpolateScenarioFile(["Output/TSPI/OS.csv", "Output/TSPI/T1.csv"])
    pass