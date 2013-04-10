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
        
        self._move_costs = {'mountain': 2,
                             'forest': 1.5,
                             'sand': 1.5}
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function for special damage
        """
        # Do bonus damage to armored vehicles
        if target.type == "Tank" or target.type == "Battleship":
            # Calculate the total damage
            damage = self.damage + self.bonus_damage
            
            # Calculate the unit's defense
            defense = target_tile.defense_bonus + target.defense
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
            
            return damage - defense
        else: return super().get_damage(target, target_tile)

unit.unit_types["Anti-Armour"] = AntiArmour
