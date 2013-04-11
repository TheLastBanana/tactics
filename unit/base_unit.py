import pygame, unit, helper, bmpfont, effects
from pygame.sprite import Sprite

FRAME_MOVE_SPEED = 3/20
SIZE = 20

class BaseUnit(Sprite):
    """
    The basic representation of a unit from which all other unit types
    extend.
    """
    
    active_units = pygame.sprite.Group()
    
    health_font = bmpfont.BitmapFont("assets/healthfont.png", 6, 7, 48)
    
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
        
        #Default unit stats
        self.health = 10
        self.max_health = self.health
        self.speed = 5
        self.atk_range = 1
        self.damage = 1
        self.defense = 3
        self.type = "Base Unit"
        self.hit_effect = None
        self.die_effect = effects.Explosion
        
        #Dictionary of movement costs by tile type name
        self._move_costs = {}
        
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
    
        # Rotate the sprite
        self.image = pygame.transform.rotate(subsurf, self._angle)

        # Render the health.
        health_surf = BaseUnit.health_font.render(str(int(self.health)))
        
        # Move the health to the bottom-right of the image.
        image_rect = self.image.get_rect()
        health_rect = health_surf.get_rect()
        health_rect.move_ip(image_rect.w - health_rect.w,
                            image_rect.h - health_rect.h)
                            
        # Draw the health on to the image.
        self.image.blit(health_surf, health_rect)
        
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
        if self._active:
            self._active = False
            BaseUnit.active_units.remove(self)
    
    @property
    def active(self):
        """
        Returns whether this is active.
        """
        return self._active
    
    @property
    def is_moving(self):
        """
        Returns whether or not a unit is currently in transit.
        """
        return self._moving
            
    def face_vector(self, vector):
        """
        Sets the unit's angle based on the given vector (dx, dy).
        Angle is snapped to 90-degree increments.
        Does not change the angle if dx == dy == 0.
        """
        dx, dy = vector
        
        # Can't choose an angle if there isn't one
        if dx == dy == 0:
            return
        
        # Set the angle
        if abs(dx) > abs(dy):
            # Horizontal
            if dx > 0:
                self.set_angle(0)
            else:
                self.set_angle(180)
        else:
            # Vertical
            if dy > 0:
                self.set_angle(270)
            else:
                self.set_angle(90)

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
                                  
                #angle properly
                self.face_vector((dx, dy))

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
        
    def set_angle(self, angle):
        """
        Sets the sprite's new angle, rotating the graphic at the same
        time. Does nothing if the sprite is already at that angle.
        """
        if self._angle == angle: return
        self._angle = angle
        self._update_image()
        
    def hurt(self, damage):
        """
        Causes damage to the unit, and destroys it when it's out of health.
        """
        self.health -= damage
        
        # Dead!
        if self.health <= 0:
            self.deactivate()
        
        # Update the health graphic.
        self._update_image()
        
    def move_cost(self, tile):
        """
        Returns the cost of a unit moving over a certain tile.
        Note: this should be greater than or equal to 1!
        
        Can be overridden for special behaviour. Make sure to use this as a
        default return value just in case.
        """
        # If this is not defined, default to the lowest possible cost.
        if tile.type not in self._move_costs:
            return 1
            
        # Otherwise, return the cost.
        return self._move_costs[tile.type]
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not a unit can move over a certain tile.
        Position is also passed so it can be checked for other units.
        
        Override this for subclasses, perhaps using this as the default value.
        """
        #If there's no tile there (i.e. mouse is off screen)
        if not tile:
            return False
        
        return True
        
    def positions_in_range(self, from_tile, from_pos):
        """
        Returns a set of all tile coordinates in range of the given tile.
        """
        from_x, from_y = from_pos
        tiles = set()
        
        # Get range
        r = self.max_atk_range
        # Add (or subtract) bonus range from occupied tile
        r += from_tile.range_bonus
        
        # Add the tiles in range. Not the most efficient way, but
        # probably the most readable.
        for x in range(int(from_x - r), int(from_x + r + 1)):
            for y in range(int(from_y - r), int(from_y + r + 1)):
                
                # Check if this is in range
                if self.is_tile_in_range(from_tile, from_pos, (x, y)):
                    tiles.add((x, y))
                    
        return tiles
        
    def is_attackable(self, from_tile, from_pos, to_tile, to_pos):
        """
        Returns whether the given tile is attackable.
        
        Override this for subclasses, perhaps using this as a default value.
        """
        # We can only attack within the unit's range.
        if not self.is_tile_in_range(from_tile, from_pos, to_pos):
            return False
        
        # Get the unit we're going to attack.
        u = BaseUnit.get_unit_at_pos(to_pos)
        
        # We can't attack if there's no unit there, or if it's on our team.
        if not u or u.team == self.team:
            return False
            
        return True
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        """
        defense =  target_tile.defense_bonus + target.defense
        
        # Don't do negative damage
        if self.damage - defense < 0:
            return 0
        
        return self.damage - defense
        
    def get_atk_range(self, tile = None):
        """
        Returns the unit's maximum attack range, assuming that it is attacking
        from the given tile. If no tile is provided, this just returns the
        unit's range.
        """
        return self.max_atk_range
        
    def is_tile_in_range(self, from_tile, from_pos, to_pos):
        """
        Checks to see if a tile is in attackable range from its current
        position. Takes tile range bonus into account.
        """
        # Get range
        r = self.max_atk_range
        # Add (or subtract) bonus range from occupied tile
        r += from_tile.range_bonus
        
        dist = helper.manhattan_dist(from_pos, to_pos)
        if dist <= r:
            return True
        return False

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
