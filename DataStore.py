class DataStore():
    def __init__(self):
        self.dataLoaded = False

        self.radarFile = ""
        self.radarSettingsFile = ""
        self.simSettingsFile = ""
        self.scenarioProcSettingFile = ""
        self.scenarioFile = ""

    def setSimFiles(self, radar, radarsettings, sim, scenariosettings):
        self.radarFile = radar
        self.radarSettingsFile = radarsettings
        self.simSettingsFile = sim
        self.scenarioProcSettingFile = scenariosettings
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
    
    def readScenarioProcSettingFileAsText(self):
        with open(self.scenarioProcSettingFile,'r') as file:
            return file.read()

    def getRadarFile(self):
        return self.radarFile
    
    def getRadarSettingsFile(self):
        return self.radarSettingsFile
    
    def getSimSettingsFile(self):
        return self.simSettingsFile
    
    def getScenarioFile(self):
        return self.scenarioFile
    
    def getScenarioProcSettingFile(self):
        return self.scenarioProcSettingFile
        
    def getDataLoaded(self):
        return self.dataLoaded

