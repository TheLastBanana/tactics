from unit.base_unit import BaseUnit
import unit
import pygame

class Tank(BaseUnit):
    def __init__(self, **keywords):
        self._base_image = pygame.image.load("assets/tank.png")

        BaseUnit.__init__(self, **keywords)

        self.angle = 0
        self.speed = 10

    def update(self):
        BaseUnit.update(self)

unit.unit_types["Tank"] = Tank
