import sys, pygame
from pygame.sprite import RenderPlain
import tiles

class GUI(RenderPlain):
    # number of GUI instances
    num_instances = 0

    def __init__(self, screen_rect, bg_color):
        """
        Initialize the display.
        screen_rect: the bounds of the screen
        bg_color: the background color
        """
        
        RenderPlain.__init__(self)
        
        if GUI.num_instances != 0:
            raise Exception("GUI: can only have one instance of a simulation")
        GUI.num_instances = 1
        
        self.screen = pygame.display.set_mode((screen_rect.w, screen_rect.h))
        self.screen_rect = screen_rect
        self.bg_color = bg_color

    def draw(self):
        """
        Render the display.
        """
        self.screen.fill(self.bg_color)
        RenderPlain.update(self)
        RenderPlain.draw(self, self.screen)
        pygame.display.flip()
