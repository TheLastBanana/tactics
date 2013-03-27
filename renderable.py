import pygame

class Renderable:
    """
    An object which can be rendered onto the screen.
    """
    def __init__(self, target=None, graphic=None):
        """
        target: the render target
        grahic: the graphic to render
        """
        self.target = target
        self.graphic = graphic
        if self.graphic:
            self.rect = pygame.Rect(self.graphic.get_rect())
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
        
    def render():
        """
        Renders the object to its target.
        """
        if self.target and self.graphic:
            self.target.blit(self.graphic, self.rect)
