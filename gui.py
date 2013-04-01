import sys, pygame
from pygame.sprite import LayeredUpdates
import tiles

MAP_WIDTH = 600
BAR_WIDTH = 200
FONT_SIZE = 16
BUTTON_HEIGHT = 50
CENTER = 100
#padding for left and top side of the bar
PAD = 6

class GUI(LayeredUpdates):
    # number of GUI instances
    num_instances = 0

    def __init__(self, screen_rect, bg_color):
        """
        Initialize the display.
        screen_rect: the bounds of the screen
        bg_color: the background color
        """
        LayeredUpdates.__init__(self)
        
        if GUI.num_instances != 0:
            raise Exception("GUI: can only have one instance of a simulation")
        GUI.num_instances = 1
        
        self.screen = pygame.display.set_mode((screen_rect.w, screen_rect.h))
        self.screen_rect = screen_rect
        self.bg_color = bg_color

        self.map = tiles.TileMap(self.screen, "assets/tiles.png", 20, 20, 30, 30)
        self.map.load_from_file("maps/empty.map")
        self.map.set_highlight((0, 0, 255, 150), self.map.find_path((0, 19), (29, 0)))
        self.add(self.map)

        #Not line height, actually font size, but conveniently the same thing
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)

    def draw(self):
        """
        Render the display.
        """
        self.screen.fill(self.bg_color)
        LayeredUpdates.update(self)
        LayeredUpdates.draw(self, self.screen)
        self.drawBar()
        pygame.display.flip()

    def drawBar(self):
        """
        Draws the info bar on the right side of the screen, polls the mouse location to find which tile is currently being hovered over.
        """
        line_num = 0
        #draw the background of the bar
        barRect = pygame.Rect(MAP_WIDTH, 0, 200, 600)
        outlineRect = pygame.Rect(MAP_WIDTH, 0, 199, 599)
        pygame.draw.rect(self.screen, (150, 150, 150), barRect)
        pygame.draw.rect(self.screen, (50, 50, 50), outlineRect, 2)

        #title for tile section
        self.draw_bar_title("TILE INFO", line_num)
        line_num += 1
        
        #Tile coordinates
        mouse_pos = pygame.mouse.get_pos()
        coords = self.map.tile_coords(mouse_pos)
        self.draw_bar_text("Coordinates: {}".format(coords), line_num)
        line_num += 1

        #Is the tile passable?
        self.draw_bar_text("Passable: {}".format(self.map.is_passable(coords)), line_num)
        line_num += 1

        #divider
        self.draw_bar_div_line(line_num)
        line_num += 1

        #title for tile section
        self.draw_bar_title("UNIT INFO", line_num)
        line_num += 1

        #test
        self.draw_bar_text("Test: {}".format(True), line_num)
        line_num += 1

        #divider
        self.draw_bar_div_line(line_num)
        line_num += 1

        self.draw_bar_button(1, "MOVE", None)
        self.draw_bar_button(2, "ATTACK", None)

    def draw_bar_text(self, text, line_num):
        """
        Draws text with a specified variable at a specifed line number.
        """
        line_text = self.font.render(text, True, (0,0,0))
        self.screen.blit(line_text, (MAP_WIDTH + PAD, FONT_SIZE * line_num + PAD))

    def draw_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = self.font.render(text, True, (0,0,0))
        self.screen.blit(title_text, (MAP_WIDTH + CENTER - (title_text.get_width()/2), FONT_SIZE * line_num + PAD))

    def draw_bar_div_line(self, line_num):
        """
        Draws a dividing line at a specified line number.
        """
        y = FONT_SIZE * line_num + FONT_SIZE//2 + PAD
        pygame.draw.line(self.screen, (50, 50, 50), (MAP_WIDTH, y), (MAP_WIDTH + BAR_WIDTH, y))

    def draw_bar_button(self, slot_num, text, reaction):
        """
        Renders a button to the bar with specified text.
        Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom of the screen.
        If the mouse is hovering over the button it is rendered in white, else rgb(50, 50, 50).

        As of right now, reaction is used for nothing, but most likely will be the reaction function
        when the button is clicked.
        """
        y = self.screen.get_height() - BUTTON_HEIGHT*slot_num
        but_rect = pygame.Rect(MAP_WIDTH, y, 200, 50)
        but_out_rect = pygame.Rect(MAP_WIDTH, y, 199, 50)

        mouse_pos = pygame.mouse.get_pos()
        if but_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (255, 255, 255), but_rect)
        else:
            pygame.draw.rect(self.screen, (150, 150, 150), but_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), but_out_rect, 2)

        but_text = self.font.render(text, True, (0,0,0))
        self.screen.blit(but_text, (MAP_WIDTH + CENTER - (but_text.get_width()/2), y + (BUTTON_HEIGHT//2) - but_text.get_height()//2))
