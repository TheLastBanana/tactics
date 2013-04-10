from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class AntiTank(GroundUnit):
    """
    Anti tank unit: an infantry unit that is especially strong against
    heavily armored gound units, but weak against others.
    """
    sprite = pygame.image.load("assets/anti_tank.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = AntiTank.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "AntiTank"
        self.speed = 4
        self.atk_range = 3
        self.damage = 3
        self.bonus_damage = 5
        self.defense = 0
        self.hit_effect = effects.Explosion
        
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
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function for special damage
        """
        if target.type == "Tank":
            damage = self.damage + self.bonus_damage
            defense = target_tile.defense + target.defense
            if (damage - defense <= 0):
                return 0
            return damage - defense
        else: return super().get_damage(target, target_tile)

unit.unit_types["AntiTank"] = AntiTank
