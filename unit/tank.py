from unit.base_unit import BaseUnit
import unit
from tiles import Tile
import pygame

class Tank(BaseUnit):
    def __init__(self, **keywords):
        self._base_image = pygame.image.load("assets/tank.png")

        BaseUnit.__init__(self, **keywords)

        self.angle = 0
        self.speed = 10
        
    def move_cost(self, tile):
        """
        Returns the cost of this unit moving over a certain tile.
        """
        if tile.type == 'plains':
            return 1
        
    def is_passable(self, tile):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        if tile.type == 'plains':
            return True
        return False

unit.unit_types["Tank"] = Tank
