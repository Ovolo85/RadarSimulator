import csv

class OutputStore:

    def __init__(self) -> None:
        self.path = "output/"
        
    def writeSimResultToDisk(self, simResult):
        keyList = list(simResult)
        headerKeys = keyList[0::2]
        dataKeys = keyList[1::2]
        print(dataKeys)

        for idx, dataKey in enumerate(dataKeys):
            with open(self.path + dataKey + ".csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(simResult[headerKeys[idx]])
                for row in simResult[dataKey]:
                    writer.writerow(row)
