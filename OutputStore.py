import csv
import os
import shutil

class OutputStore:

    def __init__(self) -> None:
        self.outputPath = "Output/"
        self.tspiPath = "Output/TSPI/"
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)
        if not os.path.exists(self.tspiPath):
            os.makedirs(self.tspiPath)

        
    def writeSimResultToDisk(self, simResult):
        keyList = list(simResult)
        headerKeys = keyList[0::2]
        dataKeys = keyList[1::2]
        
        for idx, dataKey in enumerate(dataKeys):
            with open(self.outputPath + dataKey + ".csv", "w", newline="") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(simResult[headerKeys[idx]])
                for row in simResult[dataKey]:
                    writer.writerow(row)

    def writeTSPItoDisk(self, dataNames, TSPIs):
        
        # Delete previous Output
        for filename in os.listdir(self.tspiPath):
            file_path = os.path.join(self.tspiPath, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Write Ownship TSPI in /Output/TSPI/OS.csv
        with open(self.tspiPath + "OS.csv", "w", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(dataNames)
            for row in TSPIs[0]:
                writer.writerow(row)

        # Write Target TSPIs in /Output/TSPI/Tx.csv
        for t in range(1, len(TSPIs)):
            with open(self.tspiPath + "T" + str(t) + ".csv", "w", newline="") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(dataNames)
                for row in TSPIs[t]:
                    writer.writerow(row)
        


