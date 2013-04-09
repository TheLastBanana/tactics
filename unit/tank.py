from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame
import math

class Tank(BaseUnit):
    sprite = pygame.image.load("assets/tank.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Tank.sprite

        #load the base class
        BaseUnit.__init__(self, **keywords)

        #set unit specific things.
        self.speed = 10
        self.atk_range = 2
        self.damage = 4
        
    def move_cost(self, tile):
        """
        Returns the cost of this unit moving over a certain tile.
        """
        if tile.type == 'plains':
            return 1
            
        return BaseUnit.move_cost(self, tile)
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # If there's no tile there (i.e. mouse is off screen)
        if not tile:
            return False
            
        # We can't pass through enemy units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team:
            return False
        
        if tile.type == 'plains':
            return True
        
        # Return default
        return BaseUnit.is_passable(self, tile, pos)
        
    def is_attackable(self, from_tile, from_pos, to_tile, to_pos):
        """
        Returns whether the given tile is attackable.
        """
        # We can only attack within the unit's range.
        dist = helper.manhattan_dist(from_pos, to_pos)
        if dist > self.get_atk_range(from_tile):
            return False
        
        # Get the unit we're going to attack.
        u = BaseUnit.get_unit_at_pos(to_pos)
        
        # We can't attack if there's no unit there, or if it's on our team.
        if not u or u.team == self.team:
            return False
            
        return True

unit.unit_types["Tank"] = Tank
