import sys, pygame
from pygame.sprite import LayeredUpdates
import tiles
from unit import *
import unit

MAP_WIDTH = 600
BAR_WIDTH = 200
FONT_SIZE = 16
BUTTON_HEIGHT = 50
CENTER = 100
#padding for left and top side of the bar
PAD = 6
SELECT_COLOR = (255, 255, 0, 255)

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
        self.map = None

        self.unit_group = pygame.sprite.Group()
        self.add(self.unit_group)
        self.sel_unit = None

        #Not line height, actually font size, but conveniently the same thing
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        
    def load_level(self, filename):
        """
        Loads a map from the given filename.
        """
        self.remove(self.map)
        
        map_file = open(filename, 'r')
        
        # Get the map size
        line = map_file.readline()
        w, h = [int(x) for x in line.split('x')]
        
        # Move up to the start of the map
        while line.find("MAP START") < 0:
            line = map_file.readline()
        line = map_file.readline()
            
        # Read in the map
        map_tiles = []
        while line.find("MAP END") < 0:
            line = line.rstrip()
            line = line.split(' ')
            for c in line:
                map_tiles.append(int(c))
            line = map_file.readline()
        if len(map_tiles) != w * h:
            raise Exception("Wrong number of tiles in {}!".format(filename))
        
        # Create the tile map
        self.map = tiles.TileMap("assets/tiles.png", 20, 20, w, h)
        self.map.tiles = map_tiles
        self.add(self.map)
        
        # Move up to the unit definitions
        while line.find("UNITS START") < 0:
            line = map_file.readline()
        line = map_file.readline()
        
        # Create the units
        while line.find("UNITS END") < 0:
            line = line.rstrip()
            line = line.split(' ')
            unit_name = line[0]
            x, y = int(line[1]), int(line[2])
            x, y = self.map.screen_coords((x, y))
            
            if not unit_name in unit.unit_types:
                raise Exception("No unit of name {} found!".format(unit_name))
            new_unit = unit.unit_types[unit_name]()
            new_unit.rect.x = x
            new_unit.rect.y = y
            self.unit_group.add(new_unit)
            
            line = map_file.readline()

    def on_click(self, e):
        #make sure we have focus
        if (e.type == pygame.MOUSEBUTTONUP
            and e.button == 1
            and pygame.mouse.get_focused()):
            #get the unit at the mouseclick
            unit = self.unit_at_pos(e.pos)

            #TODO, this will need to be updated once we have a concept of ownership
            # as well as attack/move states

            #clicking the same unit again deselects it
            if unit == self.sel_unit:
                self.sel_unit = None

            #update the selected unit
            elif unit and unit != self.sel_unit:
                self.sel_unit = unit
                
    def unit_at_pos(self, pos):
        """
        Gets the unit at a specified position. ((x,y) tuple).
        Returns None if no unit.
        """
        #iterate over all unit sprites
        for unit in self.unit_group.sprites():
            #determine if the click was inside the unit
            if unit.rect.collidepoint(pos):
                return unit

        #return no unit
        return None

    def draw(self):
        """
        Render the display.
        """
        # Fill in the background
        self.screen.fill(self.bg_color)
        
        # Update and draw the group contents
        LayeredUpdates.update(self)
        LayeredUpdates.draw(self, self.screen)
        
        # update and draw units
        self.unit_group.update()
        self.unit_group.draw(self.screen)
        
        # If there's a selected unit, highlight it
        if self.sel_unit:
            pygame.gfxdraw.rectangle(
                self.screen,
                self.sel_unit.rect,
                SELECT_COLOR)
        
        # Draw the status bar
        self.drawBar()

        # Update the screen
        pygame.display.flip()

    def drawBar(self):
        """
        Draws the info bar on the right side of the screen, polls the mouse
        location to find which tile is currently being hovered over.
        """
        if not self.map: return
        
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
        self.draw_bar_text(
            "Passable: {}".format(self.map.is_passable(coords)),
            line_num)
        line_num += 1

        #divider
        self.draw_bar_div_line(line_num)
        line_num += 1

        if self.sel_unit:
            #title for tile section
            self.draw_bar_title("UNIT INFO", line_num)
            line_num += 1

            #health
            health = self.sel_unit.get_health_str()
            self.draw_bar_text("Health: {}".format(health), line_num)
            line_num += 1

            #speed
            speed = self.sel_unit.get_speed_str()
            self.draw_bar_text("Speed: {}".format(speed), line_num)
            line_num += 1

            #Facing
            direction = self.sel_unit.get_direction()
            self.draw_bar_text("Facing: {}".format(direction), line_num)
            line_num += 1

            #divider
            self.draw_bar_div_line(line_num)
            line_num += 1

        self.draw_bar_button(1, "MOVE")
        self.draw_bar_button(2, "ATTACK")

    def draw_bar_text(self, text, line_num):
        """
        Draws text with a specified variable at a specifed line number.
        """
        line_text = self.font.render(text, True, (0,0,0))
        self.screen.blit(
            line_text,
            (MAP_WIDTH + PAD, FONT_SIZE * line_num + PAD))

    def draw_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = self.font.render(text, True, (0,0,0))
        self.screen.blit(
            title_text,
            (MAP_WIDTH + CENTER - (title_text.get_width()/2),
            FONT_SIZE * line_num + PAD))

    def draw_bar_div_line(self, line_num):
        """
        Draws a dividing line at a specified line number.
        """
        y = FONT_SIZE * line_num + FONT_SIZE//2 + PAD
        pygame.draw.line(
            self.screen,
            (50, 50, 50),
            (MAP_WIDTH, y),
            (MAP_WIDTH + BAR_WIDTH, y))

    def draw_bar_button(self, slot_num, text):
        """
        Renders a button to the bar with specified text.
        Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom
        of the screen.
        If the mouse is hovering over the button it is rendered in white, else
        rgb(50, 50, 50).
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
        self.screen.blit(
            but_text,
            (MAP_WIDTH + CENTER - (but_text.get_width()/2),
            y + (BUTTON_HEIGHT//2) - but_text.get_height()//2))
