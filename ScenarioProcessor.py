import json, math

from numpy import arccos, array, cos, deg2rad, mod, pi, sin, tan
import matplotlib.pyplot as plt


from Scenario import Scenario

class ScenarioProcessor:

    def __init__(self) -> None:
        self.scenario = None
        self.burstLength = None
        

    def processScenario(self, scenarioFile, radarFile):
        self.getScenarioFromJSON(scenarioFile)
        self.getRadarDataFromJSON(radarFile)

        self.ownshipPositions = []
        self.targetPositions = []
        
        # Set Start Condition for Ownship
        self.ownshipPositions.append([0.0, self.scenario.ownShipStartData["north"], 
        self.scenario.ownShipStartData["east"], 
        self.scenario.ownShipStartData["down"], 
        self.scenario.ownShipStartData["heading"], 
        self.scenario.ownShipStartData["velocity"], 
        self.scenario.ownShipStartData["pitch"]
        ])
        
        # Init Position Data for all Targets
        self.targetPositions = [[] for _ in range(len(self.scenario.targetStartData))]
        
        # Process the Targets
        for tgtNumber in range(len(self.scenario.targetStartData)):
            
            # Set Start Condition for current Target
            self.targetPositions[tgtNumber].append([0.0, 
                self.scenario.targetStartData[tgtNumber]["north"], 
                self.scenario.targetStartData[tgtNumber]["east"], 
                self.scenario.targetStartData[tgtNumber]["down"], 
                self.scenario.targetStartData[tgtNumber]["heading"], 
                self.scenario.targetStartData[tgtNumber]["velocity"], 
                self.scenario.targetStartData[tgtNumber]["pitch"]
                ])

            for man in self.scenario.targetManLists[tgtNumber]:
                if man["type"] == "static":
                    manPositions = self.processStatic(self.targetPositions[tgtNumber][-1], man)
                elif man["type"] == "gcurve":
                    manPositions = self.processGCurve(self.targetPositions[tgtNumber][-1], man)
                elif man["type"] == "constaccel":
                    manPositions = self.processConstAccel(self.targetPositions[tgtNumber][-1], man)
                elif man["type"] == "constrateclimb":
                    manPositions = self.processConstRateClimb(self.targetPositions[tgtNumber][-1], man)
                else:
                    print("Unknown Manoeuvre Type " + man["type"])
                if manPositions != None:  
                    for pos in range(1, len(manPositions)):
                        self.targetPositions[tgtNumber].append(manPositions[pos])

                        
        # Process Ownship
        for man in self.scenario.ownShipManList:
            if man["type"] == "static":
                manPositions = self.processStatic(self.ownshipPositions[-1], man)
            elif man["type"] == "gcurve":
                manPositions = self.processGCurve(self.ownshipPositions[-1], man)
            elif man["type"] == "constaccel":
                manPositions = self.processConstAccel(self.ownshipPositions[-1], man)
            elif man["type"] == "constrateclimb":
                manPositions = self.processConstRateClimb(self.ownshipPositions[-1], man)
            else:
                print("Unknown Manoeuvre Type " + man["type"])
            if manPositions != None:   
                for pos in range(1, len(manPositions)):
                    self.ownshipPositions.append(manPositions[pos])
            

        # Prepare the result to be returned
        result = []
        result.append(self.ownshipPositions)
        for tgtNumber in range(len(self.scenario.targetStartData)):
            result.append(self.targetPositions[tgtNumber])
        
        return result

    def getScenarioFromJSON(self, f):
        with open(f) as json_file:
            data = json.load(json_file)
        self.scenario = Scenario(data["ownship"], data["targets"], data["ownshipMans"], data["targetMans"])
    
    def getRadarDataFromJSON(self, f):
        with open(f) as json_file:
            data = json.load(json_file)
        self.burstLength = data["BurstLength"]

    def processConstRateClimb(self, startCondition, manoeuvre):
        #TODO: This does not yet change the Pitch
        startTime = startCondition[0]

        positions = []
        positions.append(startCondition)
        
        downChange = manoeuvre["targetdown"] - startCondition[3]
        rate = manoeuvre["rate"]
        manoeuvreTime = abs(downChange) / rate
        cycles = int(round(manoeuvreTime / self.burstLength))

        downstep = downChange / cycles
        distanceDiagonal = startCondition[5] * manoeuvreTime
        distanceProjected = math.sqrt(distanceDiagonal**2 - downChange**2)
        alongStep = distanceProjected / cycles

        for cycle in range(cycles):
            newNorth = positions[-1][1] + (cos(deg2rad(positions[-1][4])) * alongStep) 
            newEast = positions[-1][2] + (sin(deg2rad(positions[-1][4])) * alongStep)
            newDown = positions[-1][3] + downstep
            newHeading = positions[-1][4]
            newVel = positions[-1][5]
            newPitch = positions[-1][6]

            positions.append([startTime + self.burstLength*cycle, newNorth, newEast, newDown, newHeading, newVel, newPitch])

        positions.pop(0)
        return positions

    def processConstAccel(self, startCondition, manoeuvre):
        startTime = startCondition[0]

        positions = []
        positions.append(startCondition)

        time = int(manoeuvre["time"])
        velChange = int(manoeuvre["targetv"])-startCondition[5]
        velChangePerSimStep = velChange / time * self.burstLength
        velocity = startCondition[5]

        cycles = int(manoeuvre["time"] / self.burstLength)

        for cycle in range(cycles):
            velocity = velocity + velChangePerSimStep
            distance = velocity * self.burstLength

            newNorth = positions[-1][1] + (cos(deg2rad(positions[-1][4])) * distance) 
            newEast = positions[-1][2] + (sin(deg2rad(positions[-1][4])) * distance)
            newDown = positions[-1][3]
            newHeading = positions[-1][4]
            newVel = velocity
            newPitch = positions[-1][6]

            positions.append([startTime + self.burstLength*cycle, newNorth, newEast, newDown, newHeading, newVel, newPitch])

        positions.pop(0)
        return positions

        


    def processGCurve (self, startCondition, manoeuvre):
        
        startTime = startCondition[0]

        # Get Radius
        bank = arccos(1/manoeuvre["gload"])
        r = (startCondition[5] ** 2) / (9.81 * tan(bank))

        # Get Center Point
        if manoeuvre["degree"] < 0:
            centerDir = startCondition[4] - 90 
        else:
            centerDir = startCondition[4] + 90
        centerDir = mod (centerDir, 360)
        northOffset = r * cos (deg2rad (centerDir)) + startCondition[1]
        eastOffset = r * sin (deg2rad (centerDir)) + startCondition[2]
        centerToStartingPointDir = mod ((centerDir + 180), 360)

        # get Manoeuvre Time
        cf = 2*r*pi
        cfPart = abs((manoeuvre["degree"]/360)) * cf
        t = cfPart / startCondition[5]
        cycles = int(t / self.burstLength)

        anglePerCycle = abs(manoeuvre["degree"]) / cycles

        # prepare Result
        positions = []
        positions.append(startCondition)

        for cycle in range(cycles):
            currentAngle = anglePerCycle * (cycle + 1)
            
            if manoeuvre["degree"] < 0:
                currentAngleTotal = centerToStartingPointDir - currentAngle
                newHeading = positions[-1][4] - anglePerCycle 
            else:
                currentAngleTotal = centerToStartingPointDir + currentAngle
                newHeading = positions[-1][4] + anglePerCycle 

            newNorth = cos(deg2rad(currentAngleTotal)) * r + northOffset
            newEast = sin(deg2rad(currentAngleTotal)) * r + eastOffset
            newDown = positions[-1][3]

            newVel = positions[-1][5]
            newPitch = positions[-1][6]

            positions.append([startTime + self.burstLength*cycle, newNorth, newEast, newDown, newHeading, newVel, newPitch])

        positions.pop(0)
        return positions

    def processStatic (self, startCondition, manoeuvre):
        
        startTime = startCondition[0]

        positions = []
        positions.append(startCondition)
        distance = startCondition[5] * self.burstLength
        cycles = int(manoeuvre["time"] / self.burstLength)

        
        for cycle in range(cycles):
            newNorth = positions[-1][1] + (cos(deg2rad(positions[-1][4])) * distance) 
            newEast = positions[-1][2] + (sin(deg2rad(positions[-1][4])) * distance)
            newDown = positions[-1][3]
            newHeading = positions[-1][4]
            newVel = positions[-1][5]
            newPitch = positions[-1][6]

            positions.append([startTime + self.burstLength*cycle, newNorth, newEast, newDown, newHeading, newVel, newPitch])

        positions.pop(0)
        return positions

    






