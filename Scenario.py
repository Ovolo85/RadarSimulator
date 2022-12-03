class Scenario: 

# TODO: Is that in use somewhere?
    def __init__(self, ownship, targets, osmanlist, tgtsmanlist) -> None:
        self.ownShipStartData = ownship
        self.targetStartData = targets
        self.ownShipManList = osmanlist
        self.targetManLists = tgtsmanlist