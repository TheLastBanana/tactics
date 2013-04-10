from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Artillery(GroundUnit):
    """
    A jeep: lightly armored and armed, but fast.
    """
    sprite = pygame.image.load("assets/artillery.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Artillery.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Artillery"
        self.speed = 6
        self.max_atk_range = 5
        self.min_atk_range = 3
        self.damage = 7
        self.defense = 1
        self.hit_effect = effects.Explosion
        
        self._move_costs = {'plains': 1.5,
                             'road': 1,
                             'mountain': 3}
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        ttype = tile.type
        if (tile.type == 'forest'):
            return False
        
        #The tile is passable
        return True
        
    def is_tile_in_range(self, from_tile, from_pos, to_pos):
        """
        Checks to see if a tile is in attackable range from its current
        position. Takes tile range bonus into account.
        
        Overrides superclass method.
        """
        # Get range
        max_range = self.max_atk_range
        min_range = self.min_atk_range
        # Add (or subtract) bonus range from occupied tile
        max_range += from_tile.range_bonus
        
        dist = helper.manhattan_dist(from_pos, to_pos)
        if min_range <= dist and dist <= max_range:
            return True
        return False

unit.unit_types["Artillery"] = Artillery
