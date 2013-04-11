from unit.water_unit import WaterUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Carrier(WaterUnit):
    """
    An aircraft carrier. Slow, and has minimal attack, but it can refuel
    aircraft!
    """
    sprite = pygame.image.load("assets/carrier.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Carrier.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Carrier"
        self.speed = 4
        self.max_atk_range = 2
        self.damage = 3
        self.defense = 2
        self.hit_effect = effects.Ricochet

unit.unit_types["Carrier"] = Carrier
