import pygame
import unit
from pygame.sprite import Sprite

class BaseUnit(Sprite):
    """
    The basic representation of a unit from which all other unit types
    extend.
    """
    
    def __init__(self):
        self.health = 10
        self.speed = 8
        self._angle = 0
        self._base_image = pygame.image.load("assets/tank.png")
    
        Sprite.__init__(self)
        
        self.image = self._base_image
        self.rect = self.image.get_rect()
        
    def set_angle(self, angle):
        """
        Sets the sprite's new angle, rotating the graphic at the same
        time. Does nothing if the sprite is already at that angle.
        """
        if self._angle == angle: return
        self._angle = angle
        self.image = pygame.transform.rotate(self._base_image, self._angle)

unit.unit_types["Tank"] = BaseUnit
