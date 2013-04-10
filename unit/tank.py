from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Tank(GroundUnit):
    """
    A tank: heavily armed, but not especially fast.
    
    Tanks move at a constant rate over any terrain they can pass.
    """
    sprite = pygame.image.load("assets/tank.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Tank.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Tank"
        self.speed = 5
        self.max_atk_range = 2
        self.damage = 6
        self.defense = 3
        self.hit_effect = effects.Explosion
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        if (tile.type == 'wall' or
           tile.type == 'mountain' or
           tile.type == 'forest'):
            return False
        
        #The tile is passable
        return True

unit.unit_types["Tank"] = Tank
