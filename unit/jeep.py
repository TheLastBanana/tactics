from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Jeep(GroundUnit):
    """
    A jeep: lightly armored and armed, but fast.
    """
    sprite = pygame.image.load("assets/jeep.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Jeep.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Jeep"
        self.speed = 10
        self.max_atk_range = 2
        self.damage = 5
        self.defense = 1
        self.hit_effect = effects.Ricochet
        
    def move_cost(self, tile):
        """
        Returns the cost of this unit moving over a certain tile.
        """
        if tile.type == 'plains':
            return 2 
        elif (tile.type == 'sand' or
            tile.type == 'forest'):
            return 3
        elif tile.type == 'road':
            return 1
        elif tile.type == 'mountain':
            return 4
            
        return super().move_cost(tile)
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        if (tile.type == 'wall'):
            return False
        
        #The tile is passable
        return True

unit.unit_types["Jeep"] = Jeep
