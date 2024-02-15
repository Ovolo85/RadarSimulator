import csv
import numpy as np

class ScenarioInterpolator:
    
    def __init__(self, burstRate):
        self.burstRate = burstRate

    def interpolateScenario(self, scenario):
        preScenario = scenario
        postScenario = []

        for aircraftTSPI in preScenario:
            maxTime = aircraftTSPI[-1][0]
            targetTimes = np.arange(0.0, maxTime, self.burstRate)
            aircraftTSPIarray = np.array(aircraftTSPI)
            originalTimes = aircraftTSPIarray.T[0]
            postAircraftTSPI = np.array(targetTimes)
            for col in aircraftTSPIarray.T[1:]:
                colInterp = np.interp(targetTimes, originalTimes, col)
                postAircraftTSPI = np.column_stack([postAircraftTSPI, colInterp])

            postScenario.append(postAircraftTSPI.tolist())

        return postScenario



    def interpolateScenarioFile(self, scenarioFiles):
        scenario = []
        single_aircraft_scenario = []
        
        for file in scenarioFiles:
            with open(file, "r") as f:
                reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
                next(reader) # skip first line
                for row in reader:
                    single_aircraft_scenario.append(row)
            scenario.append(single_aircraft_scenario)
            single_aircraft_scenario = []
        scenario_output = self.interpolateScenario(scenario)
        return scenario_output
    
if __name__ == "__main__":
    si = ScenarioInterpolator(0.003)
    sc = si.interpolateScenarioFile(["Output/TSPI/OS.csv", "Output/TSPI/T1.csv"])
    pass