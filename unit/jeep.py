from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Jeep(GroundUnit):
    """
    A jeep: lightly armored and armed, but fast.
    """
    sprite = pygame.image.load("assets/jeep.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Jeep.sprite

        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Jeep"
        self.speed = 10
        self.max_atk_range = 2
        self.damage = 5
        self.defense = 1
        self.hit_effect = effects.Ricochet
        
        self._move_costs = {'plains': 2,
                             'sand': 3,
                             'forest': 3,
                             'road': 1,
                             'mountain': 4}

unit.unit_types["Jeep"] = Jeep
