from unit.ground_unit import GroundUnit
import unit, helper
from tiles import Tile
import pygame

class Tank(GroundUnit):
    """
    A tank: heavily armed, but not especially fast.
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
        self.atk_range = 2
        self.damage = 4
        
    def move_cost(self, tile):
        """
        Returns the cost of this unit moving over a certain tile.
        """
        if tile.type == 'plains':
            return 1
            
        return super().move_cost(tile)
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # If there's no tile there (i.e. mouse is off screen)
        if not tile:
            return False
            
        # We can't pass through enemy units.
        u = unit.base_unit.BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team:
            return False
        
        if tile.type == 'plains':
            return True
        
        # Return default
        return super().is_passable(tile, pos)

unit.unit_types["Tank"] = Tank
