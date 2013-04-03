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
        self._moving = False
    
        Sprite.__init__(self)
        
        self.image = self._base_image
        self.rect = self.image.get_rect()

    def is_moving(self):
        return self._moving
        
    def set_angle(self, angle):
        """
        Sets the sprite's new angle, rotating the graphic at the same
        time. Does nothing if the sprite is already at that angle.
        """
        if self._angle == angle: return
        self._angle = angle
        self.image = pygame.transform.rotate(self._base_image, self._angle)

    def get_speed_str(self):
        """
        Returns the unit's speed as a string.
        """
        return str(self.speed)

    def get_health_str(self):
        """
        Returns the unit's health as a string.
        """
        return str(self.health)

    def get_direction(self):
        """
        Returns the unit's angle as a cardinal direcion
            (i.e. North, South, East, West).
        """
        angle = abs(self._angle % 90)

        if angle == 0:
            return "East"
        elif angle == 90:
            return "North"
        elif angle == 180:
            return "West"
        elif angle == 270:
            return "South"
