from typing import Callable
import pygame
import json
from pathlib import Path
from GUIClasses import clickable
from GUIClasses import textInputBox
from GUIClasses import GUIElement

"""
TODO: 
NOW: 
Better shipBuilding
Assembling ships,
"""
def getSaves():
    savesFolder = Path.cwd()/"Data"/"Saves"
    return list(savesFolder.iterdir())

def save(save: dict, path: Path):
    with open(path) as saveFile:
        json.dump(save,saveFile, indent = 4)

class planet:
    """Creates a Planet. Distance must be in AU (astronomical Units)"""
    def __init__(self, name: str, backgroundImg: str, distance: int) -> None:
        self.name = name
        self.backgroundImg = backgroundImg
        self.distance = distance


class partType:
    def __init__(self, name: str, image: pygame.surface.Surface, defaultSize: tuple[int,int]) -> None:
        self.name = name
        self.image = image
        self.defaultSize = defaultSize
    
    def __call__(self) -> dict:
        return {"type":self.name}
    
    def draw(self, rect: pygame.rect.Rect, surface: pygame.surface.Surface):
        rect.topleft = scaleCoords(rect.topleft,game.shipBuilderGridSize)
        image = pygame.transform.scale(self.image,scaleCoords(self.defaultSize,game.shipBuilderGridSize))
        surface.blit(image, rect)


class gameClass:
    def __init__(self) -> None:
        self.planets = [
            planet("Earth","Graphics/Kennedy Space Centre (TEMP).png",1)
            ]
        self.GUI: list[GUIElement] = [
            GUIElement("BuyShip screen",makeCurvedRectangle(screenSize),screenSize,(0,0),lambda:self.screen == "buyShip"),
            clickable("Map Button",image("Graphics/Map Button.png"),(50,20),(420,10),self.openMap,lambda:self.screen == "planet"),
            clickable("Design Ship",image("Graphics/Design Ship Button.png"),(50,20),(420,40),self.openShipBuilder,lambda:self.screen == "planet"),
            clickable("Back Button",image("Graphics/Back Button.png"),(50,50),(10,10),returnToPlanet, lambda:not self.screen == "planet"),
            clickable("Buy Ship",image("Graphics/Buy Ship Button.png"),(50,20),(420,70),self.openShipBuyer,lambda: self.screen == "planet"),
            clickable("quit",image("Graphics/Quit Button.png"),(100,60),(190,100),closeGame,lambda: self.screen == "menu"),
            clickable("Save Ship",image("Graphics/Save Button.png"),(50,30),(400,300),startSaveShip,lambda: self.screen == "shipBuilder")
        ]
        self.partTypes = [
            partType("Command Pod",image("Graphics/command pod 1.png"),(3,3)),
            partType("Fuel Tank",image("Graphics/Fuel Tank.png"),(3,4)),
            partType("Rocket Engine",image("Graphics/Rocket engine 1.png"),(1,2))
        ]
        self.starMass = 1
        #Year is 12 minutes long
        self.yearLength = 12*60
        self.screen = "planet"
        self.actions = {
            "toggleMap":self.togglemap,
            "toggleMenu":self.toggleMenu
        }
        self.selectedPart = emptyPart
        self.shipBuilderGridSize = int(360/30)
        for i,part in enumerate(self.partTypes):
            self.GUI.append(clickable(
                part.name,
                part.image,
                (int(self.shipBuilderGridSize*3*part.defaultSize[0]/part.defaultSize[1]),self.shipBuilderGridSize*3),
                (420,10+i*(10+self.shipBuilderGridSize*3)),
                selectPartGenerator(part),
                lambda:self.screen == "ShipBuilder"))
        self.shipBuilderGridSize = int(screenSize[1]/30)

    def drawBackground(self,planet:int) -> None:
        #get background
        background = pygame.image.load(self.planets[planet].backgroundImg)
        background = pygame.transform.scale(background,screenSize)

        #render Background
        screen.blit(background,(0,0))

    def drawMap(self):
        systemMap = pygame.Surface((screenSize))
        systemMap.fill((0,0,0))
        pixelsPerAU = (screenSize[1]*0.875)/max([planet.distance for planet in game.planets])/2
        centre = (screenSize[0]//2,screenSize[1]//2)
        #TODO: find sun radius automatically
        pygame.draw.circle(systemMap,(255,255,128),centre,screenSize[0]/200)
        for planet in game.planets:
            #print(f"Drawing planet {planet.name} at a distance of {planet.distance}")
            pygame.draw.circle(systemMap,(255,255,255),centre,(planet.distance*pixelsPerAU),2)
        screen.blit(systemMap,(0,0))

    def drawShipBuilder(self):
        #Draw Background (blueprint grid)
        shipBuilder = pygame.Surface((screenSize))
        shipBuilder.fill((51, 212, 201))
        self.shipBuilderGridSize = int(screenSize[1]/30)
        gridSize = self.shipBuilderGridSize
        numVerticalLines = 30
        numHorizontalLines = 30
        for x in range(gridSize,gridSize*numVerticalLines+1,gridSize):
            pygame.draw.line(shipBuilder,(255,255,255),(x,gridSize),(x,gridSize*numHorizontalLines))
        for y in range(gridSize,gridSize*numHorizontalLines+1,gridSize):
            pygame.draw.line(shipBuilder,(255,255,255),(gridSize,y),(gridSize*numVerticalLines,y))
        screen.blit(shipBuilder, (0,0))
        #Draw Selected Part
        if self.selectedPart is not emptyPart:
            self.selectedPart.draw(pygame.rect.Rect(scaleCoords(pygame.mouse.get_pos(),1/gridSize),self.selectedPart.defaultSize),screen)

    def drawGUI(self):
        for item in self.GUI:
            item.draw(screen,screenSize)
    
    def openMap(self):
        self.screen = "map"
        print("Map openned")
    def closeMap(self):
        self.screen = "planet"
    def togglemap(self):
        if self.screen == "planet":
            self.openMap()
        elif self.screen == "map":
            self.closeMap()
    def toggleMenu(self):
        if self.screen == "menu":
            self.screen = "planet"
        else:
            self.screen = "menu"
    def openShipBuilder(self):
        self.screen = "shipBuilder"
        global shipInVab
        shipInVab = shipBlueprint()
    def openShipBuyer(self):
        self.screen = "buyShip"

def shipBlueprint(nextStage: list = []) -> dict:
    blueprint = {}
    blueprint["nextStage"] = nextStage
    blueprint["size"] = []
    blueprint["parts"] = []
    return blueprint

def drawShip(ship: dict):
    shipImage = pygame.surface.Surface(screenSize,flags = pygame.SRCALPHA)
    for part in ship["parts"]:
        findPartType(part).draw(pygame.rect.Rect(part["position"],findPartType(part).defaultSize),shipImage)
    return shipImage

def getStats(ship: dict):
    pass

def startSaveShip():
    print("saving Ship")
    global textBox
    font = pygame.font.Font(None, 100)
    textBox = textInputBox(pygame.rect.Rect((130,130),(100,10)),font,(0,0,0),(255,255,255))

def makeShipDrawable(ship:dict):   
    

    #The code below is almost completely useless
    minX = min((part["position"][0] for part in ship["parts"]))
    miny = min((part["position"][1] for part in ship["parts"]))
    for part in ship["parts"]:
        part["position"] = [part["position"][0]-minX,part["position"][1]-miny]
    ship["size"] = [max((part["position"][0]+findPartType(part).defaultSize[0] for part in ship["parts"])),
                    max((part["position"][1]+findPartType(part).defaultSize[1] for part in ship["parts"]))]
    return ship

def completeSaveShip(name: str):
    global shipInVab
    with open(f"Data/Blueprints/{name}.json","w") as f:
        json.dump(shipInVab,f,indent=4)
    returnToPlanet()

def updateShipList():
    shipsFolder = Path.cwd()/"Data"/"Blueprints"
    for ship in shipsFolder.iterdir():
        print(ship.name.removesuffix(".json"))
        with open(ship) as shipFile:
            shipDict = json.load(shipFile)
            game.GUI.append(clickable(
                ship.name.removesuffix(".json"),
                drawShip(shipDict),
                (50,50),
                (0,0),
                buyShipGenerator(shipDict),
                lambda: game.screen == "buyShip"
            ))

def buyShipGenerator(ship: dict):
    def buyShip():
        pass
    return buyShip

def findPartType(part):
    for partType in game.partTypes:
        if part["type"] == partType.name:
            return partType

def selectPartGenerator(part: partType):
    def selectPart():
        game.selectedPart = part
    return selectPart

def eventHandler():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closeGame()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clickHandler(event)
        if event.type == pygame.KEYDOWN:
            keyboardHandler(event)

def makeCurvedRectangle(size: tuple[int,int]):
    image = pygame.surface.Surface(size)
    pygame.draw.rect(image,(51, 212, 201),pygame.rect.Rect((0,0),size),border_radius=5)
    return image

def keyboardHandler(event):
    print(event)
    global textBox
    if textBox is not None:
        if textBox.update(event.unicode):
            completeSaveShip(textBox.text)
            updateShipList()
            textBox = None
    for action, key in settings["keybinds"].items():
        if (event.unicode == key) or (event.unicode == '\x1b' and key == "esc"):
            game.actions[action]()

def clickHandler(event: pygame.event.Event):
    #Debug
    # print(event)
    # print(event.pos)
    x,y = event.pos
    if game.screen == "ShipBuilder" and not game.selectedPart == emptyPart:
        placePart()
        game.selectedPart = emptyPart
    for item in game.GUI:
        if isinstance(item,clickable) and item.getHitbox(screenSize).collidepoint(x,y) and item.condition():
            item.function()

def placePart():
    global shipInVab
    shipInVab["parts"].append(game.selectedPart())

def scaleFromScreenSize(coordinates: tuple[int,int]):
    return (int(coordinates[0]*480/screenSize[0]),int(coordinates[1]*360/screenSize[1]))

def scaleCoords(coords: tuple[int,int],scaleFactor: int):
    return (int(coords[0]*scaleFactor),int(coords[1]*scaleFactor))

def returnToPlanet():
    game.screen = "planet"

def resetSettings():
    global settings
    with open("Data/defaultSettings.json") as f:
        settings = json.load(f)
    with open("Data/settings.json","w") as f:
        json.dump(settings,f)

def image(path: str):
    return pygame.image.load(path)

def closeGame():
    global running
    running = False
    pygame.quit()
    with open("Data/settings.json","w") as f:
        json.dump(settings,f, indent=4)
    exit()

#Variable init
running = True
pygame.init()
screen = pygame.display.set_mode(flags = pygame.RESIZABLE)
screenSize = pygame.display.get_window_size()
pygame.display.set_caption("Python Space Program")
currentPlanet = 0
clock = pygame.time.Clock()
emptyPart: partType = partType("",pygame.Surface((1,1)),(1,1))
with open("Data/settings.json") as f:
    settings = json.load(f)
game = gameClass()
shipInVab = shipBlueprint()
textBox = None
updateShipList()
#Main code
while running:
    if not screenSize == pygame.display.get_window_size():
        print("OH NO. This shouldn't happen.")
    clock.tick(settings["framerate"])
    #Rendering Handler
    
    if game.screen == "map":
        game.drawMap()
    elif game.screen == "menu":
        screen.fill((0,0,0))
    elif game.screen == "ShipBuilder":
        game.drawShipBuilder()
        screen.blit(drawShip(shipInVab),(0,0))
    else:
        game.drawBackground(currentPlanet)
    if textBox is not None:
        textBox.draw(screen,screenSize)
    game.drawGUI()
    eventHandler()
    pygame.display.flip()