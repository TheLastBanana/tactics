from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame
import math

class GroundUnit(BaseUnit):
    """
    The basic ground-moving unit.
    """
    sprite = pygame.image.load("assets/tank.png")
    
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Ground Unit"
        
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
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, GroundUnit):
            return False
        
        if tile.type == 'water':
            return False
        
        # Return default
        return super().is_passable(tile, pos)
