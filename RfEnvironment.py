class RfEnvironment:
    
    def __init__(self, scenario) -> None:
        self.scenario = scenario

    def measure(self, prf, pw, az, el):
        print([prf, pw, az, el])