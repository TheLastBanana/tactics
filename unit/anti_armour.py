from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class AntiArmour(GroundUnit):
    """
    An infantry unit armed with an anti-armour missile launcher. Very 
    effective against tanks and battleships, but otherwise not especially
    powerful.
    
    Armour: None
    Speed: Low
    Range: Medium
    Damage: Medium (High against armoured vehicles)
    
    Other notes:
    - Slightly slowed by forests and sand.
    - Slowed somewhat more by mountains.
    - Can move through any land terrain.
    - Can't hit air units.
    """
    sprite = pygame.image.load("assets/anti_armour.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = AntiArmour.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.move_sound = "FeetMove"
        self.hit_sound = "RocketLaunch"

        #set unit specific things.
        self.type = "Anti-Armour"
        self.speed = 4
        self.max_atk_range = 3
        self.damage = 4
        self.bonus_damage = 4
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
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
            
            return damage - defense
        else: return super().get_damage(target, target_tile)
        
    def is_attackable(self, from_tile, from_pos, to_tile, to_pos):
        """
        Returns whether the given tile is attackable.
        
        Overrides this to deal with not being able to hit air units.
        """        
        # Get the unit we're going to attack.
        u = unit.base_unit.BaseUnit.get_unit_at_pos(to_pos)
        
        # Can't hit an air unit.
        if u and isinstance(u, unit.air_unit.AirUnit):
            return False
            
        return super().is_attackable(from_tile,
                                     from_pos,
                                     to_tile,
                                     to_pos)

unit.unit_types["Anti-Armour"] = AntiArmour
