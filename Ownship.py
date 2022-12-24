
import json


class Ownship:

    def __init__(self, scenario, radarFile) -> None:
        self.scenario = scenario
        self.getRadarDataFromJSON(radarFile)

    def getOwnshipSpeed(self, time):
        timeStep = round(time / self.burstLength)
        return self.scenario[0][timeStep][5]

    def getOwnshipHeading(self, time):
        timeStep = round(time / self.burstLength)
        return self.scenario[0][timeStep][4]

    def getOwnshipNED(self, time):
        timeStep = round(time / self.burstLength)
        return [self.scenario[0][timeStep][1], self.scenario[0][timeStep][2], self.scenario[0][timeStep][3]]

    def getRadarDataFromJSON(self, radarFile):
        with open(radarFile) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]
   