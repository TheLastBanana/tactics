import pygame
import unit
import helper
from pygame.sprite import Sprite

FRAME_MOVE_SPEED = 3/20
SIZE = 20

class BaseUnit(Sprite):
    """
    The basic representation of a unit from which all other unit types
    extend.
    """
    
    active_units = set()
    
    def __init__(self,
                 team = -1,
                 tile_x = None,
                 tile_y = None,
                 angle = 0,
                 activate = False,
                 **keywords):

        Sprite.__init__(self)
        
        #Take the keywords off
        self.team = team
        self.tile_x = tile_x
        self.tile_y = tile_y
        self._angle = angle
        
        #Some default values so that nothing complains when trying to
        #assign later
        self._moving = False
        self._active = False
        self._path = []
        self.turn_state = [False, False]
        
        #set required pygame things.
        self.image = None
        self.rect = pygame.Rect(0, 0, SIZE, SIZE)
        self._update_image()
        
        if activate:
            self.activate()
            
    @staticmethod
    def get_unit_at_pos(pos):
        """
        Returns the active unit at the given tile position, or None if no unit
        is present.
        """
        for u in BaseUnit.active_units:
            if (u.tile_x, u.tile_y) == pos:
                return u
        
        return None
                
    def _update_image(self):
        """
        Re-renders the unit's image.
        """
        # Pick out the right sprite depending on the team
        subrect = pygame.Rect(self.team * SIZE,
                              0,
                              self.rect.w,
                              self.rect.h)
        try:
            subsurf = self._base_image.subsurface(subrect)
        except:
            raise Exception(
                "Class {} does not have a sprite for team {}!".format(
                    self.__class__.__name__, self.team))
        self.image = pygame.transform.rotate(subsurf, self._angle)
        
    def activate(self):
        """
        Adds this unit to the active roster.
        """
        if not self._active:
            self._active = True
            BaseUnit.active_units.add(self)
    
    def deactivate(self):
        """
        Removes this unit from the active roster.
        """
        if self.active:
            self._active = False
            BaseUnit.active_units.remove(self)

    def update(self):
        """
        Overrides the update function of the Sprite class.
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
                if (self.tile_x, self.tile_y) == self._path[0]:
                    self._path.pop(0)
                    if not self._path: return

                #get values for calcs
                path_x, path_y = self._path[0]

                #determine deltas
                dx = helper.clamp(path_x - self.tile_x,
                                  -FRAME_MOVE_SPEED,
                                  FRAME_MOVE_SPEED)
                dy = helper.clamp(path_y - self.tile_y,
                                  -FRAME_MOVE_SPEED,
                                  FRAME_MOVE_SPEED)
                
                #by definition, units can only move horizontally or
                #vertically, never diagonally, therefore if the unit
                #is still moving then only one of these conditions
                #will ever occur
                if dx > 0:
                    self.set_angle(0)
                elif dy < 0:
                    self.set_angle(90)
                elif dx < 0:
                    self.set_angle(180)
                elif dy > 0:
                    self.set_angle(270)

                #set the new value
                self.tile_x += dx
                self.tile_y += dy

    def set_path(self, path):
        """
        Tells the unit that it should be moving, where, and how.
        """
        #if it's an empty path ignore it.
        if not path: return

        #notify that we're moving
        self._moving = True

        #get rid of the starting position.
        path.pop(0)

        #set the path
        self._path = path
        
    def move_cost(self, tile):
        """
        Returns the cost of a unit moving over a certain tile.
        
        Override this for subclasses, perhaps using this as the default value.
        """
        return 1
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not a unit can move over a certain tile.
        Position is also passed so it can be checked for other units.
        
        Override this for subclasses, perhaps using this as the default value.
        """
        #If there's no tile there (i.e. mouse is off screen)
        if not tile:
            return False
        
        return tile.passable
        
    def is_moving(self):
        """
        Returns whether or not a unit is currently in transit.
        """
        return self._moving
        
    def set_angle(self, angle):
        """
        Sets the sprite's new angle, rotating the graphic at the same
        time. Does nothing if the sprite is already at that angle.
        """
        if self._angle == angle: return
        self._angle = angle
        self._update_image()

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
        angle = abs(self._angle % 360)

        if angle == 0:
            return "East"
        elif angle == 90:
            return "North"
        elif angle == 180:
            return "West"
        elif angle == 270:
            return "South"
