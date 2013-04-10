from unit.water_unit import WaterUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Battleship(WaterUnit):
    """
    A battleship: basically, the tank of the ocean. It has high range so it can
    hit land targets.
    """
    sprite = pygame.image.load("assets/battleship.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Battleship.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Battleship"
        self.speed = 4
        self.max_atk_range = 4
        self.damage = 6
        self.defense = 3
        self.hit_effect = effects.Explosion

unit.unit_types["Battleship"] = Battleship
