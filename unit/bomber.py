from unit.air_unit import AirUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Bomber(AirUnit):
    """
    A bombing plane. Moves at medium pace, and needs to refuel 
    constantly. Good at destroying land units, mediocre at destroying 
    water units and bad at destroying other air units.
    
    Armour: High
    Speed: High
    Range: Very Low
    Damage: Medium
    Fuel: Medium
    
    Other notes:
    - The bomber has a medium amount of fuel. Players must still make
      well-planned bombing runs to ensure they can get back to the
      carrier in time.
    - When firing at ground and water units this unit does more damage.
    - Can't hit air units.
    """
    sprite = pygame.image.load("assets/bomber.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Bomber.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.hit_sound = "BombDrop"

        #set unit specific things.
        self.type = "Bomber"
        self.speed = 10
        self.max_atk_range = 1
        self.damage = 4
        self.defense = 4
        self.bonus_land_damage = 4
        self.bonus_water_damage = 3
        self.max_fuel = 12
        self.set_fuel(self.max_fuel)
        self.min_move_distance = 4
        self.hit_effect = effects.Explosion
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function to allow
        special damage effects.
        """
        # Do bonus damage to land units
        if isinstance(target, unit.ground_unit.GroundUnit):
            # Calculate the total damage
            damage = self.damage + self.bonus_land_damage
            
            # Get the unit's current defense
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
                
            return damage - defense
            
        # Do (less) bonus damage to water units
        elif isinstance(target, unit.water_unit.WaterUnit):
            # Calculate the total damage
            damage = self.damage + self.bonus_water_damage
            
            # Get the unit's current defense
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
                
            return damage - defense

        # Enemy is an air unit, how did you even manage to get here?
        else: 
            return 0
        
    def is_attackable(self, from_tile, from_pos, to_tile, to_pos):
        """
        Returns whether the given tile is attackable.
        
        Overrides this to deal with not being able to hit air units.
        """        
        # Get the unit we're going to attack.
        u = unit.base_unit.BaseUnit.get_unit_at_pos(to_pos)
        
        # Can't bomb an air unit.
        if u and isinstance(u, unit.air_unit.AirUnit):
            return False
            
        return super().is_attackable(from_tile,
                                     from_pos,
                                     to_tile,
                                     to_pos)

unit.unit_types["Bomber"] = Bomber
