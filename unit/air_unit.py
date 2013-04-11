from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame

AIR_LAYER = 5

class AirUnit(BaseUnit):
    """
    The basic air-moving unit. Runs out of fuel and needs to dock.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Air Unit"
        
    def activate(self):
        """
        Adds this unit to the active roster. Sets it to a higher layer so that
        it draws on top of other units.
        """
        super().activate()
        BaseUnit.active_units.change_layer(self, AIR_LAYER)
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # Return default
        if not super().is_passable(tile, pos):
            return False
            
        # We can't pass through enemy air units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, AirUnit):
            return False

        # Air units can pass over everything else
        return True

