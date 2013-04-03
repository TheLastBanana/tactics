import pygame
import unit
import helper
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
        
        self._path = []

        self.image = self._base_image
        self.rect = self.image.get_rect()

    def update(self):
        """
        Overrides the update function.
        Handles movement.
        """
        if self._moving:
            #checks if path is empty
            if not self._path:
                #notify not moving
                self._moving = False
                return

            #There's a path to move on
            else:
                #If we're at the next tile remove it
                if self.rect.topleft == self._path[0]:
                    self._path.pop(0)

                #get values for calcs
                path_x, path_y = self._path[0]
                rect_x, rect_y = self.rect.topleft

                #determine deltas
                dx = helper.clamp(path_x - rect_x, -3, 3)
                dy = helper.clamp(path_y - rect_y, -3, 3)

                #set the new value
                new_val = (rect_x + dx, rect_y + dy)
                self.rect.topleft = new_val
                

    def set_path(self, path):
        """
        Tells the unit that it should be moving.
        """
        #if it's an empty path ignore it.
        if not path: return

        #notify that we're moving
        self._moving = True

        #get rid of the starting position.
        path.pop(0)

        #set the path
        self._path = path
        
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
