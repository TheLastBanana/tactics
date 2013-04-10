from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class AntiArmour(GroundUnit):
    """
    Anti tank unit: an infantry unit that is especially strong against
    heavily armored gound units, but weak against others.
    """
    sprite = pygame.image.load("assets/anti_armour.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = AntiArmour.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Anti-Armour"
        self.speed = 4
        self.max_atk_range = 3
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
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        if (tile.type == 'wall'):
            return False
        
        #The tile is passable
        return True
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function for special damage
        """
        if target.type == "Tank":
            damage = self.damage + self.bonus_damage
            defense = target_tile.defense_bonus + target.defense
            if (damage - defense <= 0):
                return 0
            return damage - defense
        else: return super().get_damage(target, target_tile)

unit.unit_types["Anti-Armour"] = AntiArmour
