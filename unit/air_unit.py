from unit.base_unit import BaseUnit
from unit.carrier import Carrier
import unit, helper
from tiles import Tile
import pygame

# Layer of air units
AIR_LAYER = 5

# Rectangle for fuel indicator
FUEL_RECT = pygame.Rect(1, 1, 8, 5)

# Percentage of fuel remaining before the indicator changes colour

# Indicator colours
FUEL_BAD_CUTOFF = 1
FUEL_BACK_COLOUR = (0, 0, 0, 255)
FUEL_BACK_COLOUR_BAD = (255, 0, 0, 255)
FUEL_FILL_COLOUR = (0, 180, 0, 255)
FUEL_FILL_COLOUR_HALF = (180, 255, 0, 255)

class AirUnit(BaseUnit):
    """
    The basic air-moving unit. Runs out of fuel and needs to dock.
    """
    def __init__(self, **keywords):
        #Number of turns worth of remaining fuel.
        self.max_fuel = 6
        self._fuel = self.max_fuel
        
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Air Unit"
        
    @property
    def fuel(self):
        """
        The unit's remaining fuel.
        """
        return self._fuel
        
        
    def _update_image(self):
        """
        Redraws the unit's image.
        """
        super()._update_image()
        
        # Determine percent of fuel remaining
        fuel_percent = self.fuel / self.max_fuel
        
        # Get the rectangle for the inside of the indicator
        inner_rect = pygame.Rect(FUEL_RECT.left + 1,
                                 FUEL_RECT.top + 1,
                                 FUEL_RECT.width - 2,
                                 FUEL_RECT.height - 2)
        
        # Shrink it depending on the amount of fuel remaining
        inner_rect.w -= inner_rect.w * (1 - fuel_percent)
        
        # Determine the colours to use
        if self.fuel > FUEL_BAD_CUTOFF:
            back = FUEL_BACK_COLOUR
        else:
            back = FUEL_BACK_COLOUR_BAD
        
        if fuel_percent > 0.5:
            fill = FUEL_FILL_COLOUR
        else:
            fill = FUEL_FILL_COLOUR_HALF
        
        # Draw the indicator
        pygame.gfxdraw.box(self.image, FUEL_RECT, back)
        pygame.gfxdraw.box(self.image, inner_rect, fill)
        
    def activate(self):
        """
        Adds this unit to the active roster. Sets it to a higher layer so that
        it draws on top of other units.
        """
        super().activate()
        BaseUnit.active_units.change_layer(self, AIR_LAYER)
        
    def is_adj_to_carrier(self):
        """
        Checks if the unit is currently adjacent to a carrier.
        """
        for u in BaseUnit.active_units:
            if (isinstance(u, Carrier) and
                helper.manhattan_dist(
                    (u.tile_x, u.tile_y),
                    (self.tile_x, self.tile_y)) <= 1):
                # This is an adjacent carrier! Rejoice!
                return True
        
        # No carriers
        return False
        
    def set_fuel(self, fuel):
        """
        Changes the fuel amount and updates the graphic.
        """
        self._fuel = fuel
        self._update_image()
        
    def can_turn_end(self):
        """
        Returns whether the player turn can end.
        """
        # We haven't moved, and we aren't docked, so we can't finish the turn
        if not self.turn_state[0] and not self.is_adj_to_carrier():
            return False
        
        # Default to the superclass
        return super().can_turn_end()
        
    def turn_ended(self):
        """
        Called when the turn is ended. Runs the aircraft out of fuel, or refuels
        if there's a carrier nearby.
        """
        super().turn_ended()
        
        # Refuel at carriers
        if self.is_adj_to_carrier():
            self.set_fuel(self.max_fuel)
            return True
        
        # Decrease fuel each turn
        self.set_fuel(self.fuel - 1)
        
        # Die if we're out of fuel
        if self.fuel <= 0:
            self.hurt(self.max_health)
            return False
            
        return True
        
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
