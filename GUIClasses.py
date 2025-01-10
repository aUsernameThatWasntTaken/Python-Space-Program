from typing import Callable
from pygame import Surface
from pygame.rect import Rect
from pygame.transform import scale
from pygame.font import Font

class GUIElement:
    def __init__(self, 
                 name: str,
                 image: Surface,
                 size: tuple[int,int], 
                 origin: tuple[int,int],
                 condition: Callable[[],bool] = lambda : True,
                 ) -> None:
        self.name = name
        if image is None:
            raise ValueError(f"Image cannot be None. GUIElement \"{name}\" has invalid image")
        self.image = image
        self.size = size
        self.hitbox = Rect(origin[0],origin[1],size[0],size[1])
        self.origin = origin
        self.condition = condition

    def getHitbox(self,screenSize):
        size = scaleToScreenSize(self.size,screenSize)
        origin = scaleToScreenSize(self.origin,screenSize)
        return Rect(origin[0],origin[1],size[0],size[1])

    def draw(self,screen: Surface,screenSize: tuple[int,int]):
        if self.condition():
            screen.blit(scale(self.image,scaleToScreenSize(self.size,screenSize)),scaleToScreenSize(self.origin,screenSize))

class clickable(GUIElement):
    def __init__(self, name:str, 
                 image: Surface, 
                 size: tuple[int,int], 
                 origin: tuple[int,int],
                 function: Callable, 
                 condition: Callable[[],bool] = lambda : True,
                 ) -> None:
        super().__init__(name, image, size, origin,condition)
        self.function = function

class textInputBox:
    def __init__(self,rect: Rect,font: Font,textColour: tuple[int,int,int], colour: tuple[int,int,int]):
        self.rect = rect
        self.font = font
        self.colour = colour
        self.textColour = textColour
        self.text = ""
    
    def update(self,key: str):
        """Returns True when User presses enter"""
        if key == "\x08":
            self.text = self.text[:-1]
        if key == "\r":
            return True
        else:
            self.text += key
            return False
    
    def draw(self,screen: Surface,screenSize: tuple[int,int]):
        image = Surface(scaleCoords(self.rect.size,10))
        image.fill(self.colour)
        text = self.font.render(self.text,True,self.textColour)
        image.blit(text,(0,0))
        screen.blit(scale(image,scaleToScreenSize(self.rect.size,screenSize)),scaleToScreenSize(self.rect.topleft,screenSize))
        

def scaleToScreenSize(coordinates: tuple[int,int],screenSize: tuple[int,int]):
    return (int(coordinates[0]/480*screenSize[0]),int(coordinates[1]/360*screenSize[1]))

def scaleCoords(coords: tuple[int,int],scaleFactor: int):
    return (int(coords[0]*scaleFactor),int(coords[1]*scaleFactor))