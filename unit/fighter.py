from unit.air_unit import AirUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Fighter(AirUnit):
    """
    A fighter jet. Moves fast, but needs to refuel constantly.
    
    Armour: High
    Speed: Very High
    Range: Medium
    Damage: Medium
    Fuel: Low
    
    Other notes:
    - In order to maintain its high speed, the fighter has fairly low fuel.
      Make well-planned strafing runs and be sure you can get back to a carrier
      in time!
    """
    sprite = pygame.image.load("assets/fighter.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Fighter.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Fighter"
        self.speed = 16
        self.max_atk_range = 4
        self.damage = 5
        self.defense = 3
        self.max_fuel = 7
        self.set_fuel(self.max_fuel)
        self.min_move_distance = 6
        self.hit_effect = effects.Ricochet

unit.unit_types["Fighter"] = Fighter
