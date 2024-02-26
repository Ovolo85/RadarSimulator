import json
import os
import csv

import numpy as np

from DataStore import DataStore


class InputHandler:
    
    def __init__(self, dataStore : DataStore):
        self.dataStore = dataStore
        

    def readTSPIfromDisk(self):
        tspiPath = self.dataStore.getTSPIinputPath()
        dataSequence = self.getTSPIdataSequence()
        
        ownshipFilename = ""
        targetFilenames = []


        for filename in os.listdir(tspiPath):
            if str(filename).endswith("csv"):
                if str(filename)[0].lower() == "o":
                    ownshipFilename = filename
                elif str(filename)[0].lower() == "t":
                    targetFilenames.append(filename)

        scenario = []

        # OWNSHIP
        scenario.append(self.readSingleTSPIFile(ownshipFilename, tspiPath, dataSequence))

        # TARGETs
        for t in targetFilenames:
            scenario.append(self.readSingleTSPIFile(t, tspiPath, dataSequence))

        return scenario


    def readSingleTSPIFile(self, fileName, path, dataSequence):    
            with open(path + fileName, "r") as f:
                data = []

                reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)

                header = next(reader)
                for row in reader:
                    data.append(row)
            
            # check if data is missing in csv
            dataPresent = []
            for datum in dataSequence:
                if datum in header:
                    dataPresent.append(True)
                else:
                    dataPresent.append(False)

            # find targetColumn for each datum in the csv Header
            targetCols = []
            for h in header: 
                for idx, datum in enumerate(dataSequence):
                    if datum == h:
                        targetCols.append(idx)
                        break

            dataArray = np.array(data)
            dataArraySorted = np.zeros([len(data), len(dataPresent)])

            for idx, targetCol in enumerate(targetCols):
                dataArraySorted[:,targetCol] = dataArray[:, idx] 

            dataSortedAsList = dataArraySorted.tolist()
            
            return dataSortedAsList

    def getTSPIdataSequence(self):
        simSettingsFile = self.dataStore.getSimSettingsFile()
        with open(simSettingsFile) as json_file:
            data = json.load(json_file)

        return data["tspiDataSequence"]
    
if __name__ == "__main__":
    ds = DataStore()
    ds.setSimFiles("", "", "sim.json", "scenario_proc_setting.json")

    ih = InputHandler(ds)
    ih.readTSPIfromDisk("Input/")