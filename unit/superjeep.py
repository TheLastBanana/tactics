from unit.jeep import Jeep
import unit, helper, effects
from tiles import Tile
import pygame

class SuperJeep(Jeep):
    """
    An incredibly fast jeep: like a jeep, but it moves way further.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Incredibly Fast Jeep"
        self.speed = 100

unit.unit_types["SuperJeep"] = SuperJeep
