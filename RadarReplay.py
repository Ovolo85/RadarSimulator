import pygame
import json
import sys

class RadarReplay:

    def __init__(self, replayDataFile) -> None:
        pygame.init()

        self.getReplayDataFromJSON(replayDataFile)

        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        self.run()
       
    def run(self):
        backgroundColor = 0, 0, 0
        
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
            
            self.screen.fill(backgroundColor)
            #screen.blit(ball, ballrect)
            pygame.display.flip()

            self.clock.tick(self.framerate)

        pygame.quit()

    def getReplayDataFromJSON(self, replayDataFile):
        with open(replayDataFile) as json_file:
            data = json.load(json_file)

        self.size = data["Size"]
        self.framerate = data["Framerate"]

if __name__ == "__main__":
    a = RadarReplay("replay.json")
