import sys, pygame
from pygame.sprite import LayeredUpdates
from collections import namedtuple
import tiles, unit
from unit import *

MAP_WIDTH = 600
BAR_WIDTH = 200
FONT_SIZE = 16
BUTTON_HEIGHT = 50
CENTER = 100

# padding for left and top side of the bar
PAD = 6

# RGBA colors for grid stuff
SELECT_COLOR = (255, 255, 0, 255)
MOVE_COLOR = (0, 0, 255, 255)

# RGB colors for the GUI
FONT_COLOR = (0, 0, 0)
BAR_COLOR = (150, 150, 150)
OUTLINE_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (255, 255, 255)

# A container class which stores button information.
# Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom
# of the screen.
Button = namedtuple('Button', ['slot', 'text', 'onClick'])

class GUI(LayeredUpdates):
    # number of GUI instances
    num_instances = 0
            
    def move_pressed(self):
        """
        This is called when the move button is pressed.
        """
        # If there no unit selected, nothing happens.
        if not self.sel_unit: return
        
        # Determine where we can move.
        pos = self.map.tile_coords(
            (self.sel_unit.rect.x, self.sel_unit.rect.y))
        movable = self.map.reachable_tiles(pos,
                                           self.sel_unit.speed,
                                           self.sel_unit.move_cost,
                                           self.sel_unit.is_passable)
        
        # Highlight those squares
        self.map.clear_highlights()
        self.map.set_highlight(MOVE_COLOR, movable)
            
    def attack_pressed(self):
        """
        This is called when the attack button is pressed.
        """
        print("BOOM")

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
        
        # Set up the screen
        self.screen = pygame.display.set_mode((screen_rect.w, screen_rect.h))
        self.screen_rect = screen_rect
        self.bg_color = bg_color
        self.map = None

        # Set up unit information
        self.unit_group = pygame.sprite.Group()
        self.sel_unit = None
        
        # This directory keeps track of the unit in each tile
        # key = tile position, value = unit
        self._unit_directory = {}
        
        # Set up GUI
        self.buttons = [
            Button(0, "MOVE", self.move_pressed),
            Button(1, "ATTACK", self.attack_pressed)]

        # Not line height, actually font size, but conveniently the same thing
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
        
        # Make an empty unit directory.
        self._unit_directory.clear()
        for x in range(w):
            for y in range(h):
                self._unit_directory[(x, y)] = None
        
        # Create the units
        while line.find("UNITS END") < 0:
            line = line.rstrip()
            line = line.split(' ')
            unit_name = line[0]
            x, y = int(line[1]), int(line[2])
            screen_x, screen_y = self.map.screen_coords((x, y))
            
            if not unit_name in unit.unit_types:
                raise Exception("No unit of name {} found!".format(unit_name))
            new_unit = unit.unit_types[unit_name]()
            new_unit.rect.x = screen_x
            new_unit.rect.y = screen_y
            self.unit_group.add(new_unit)
            self._move_unit(new_unit, (x, y))
            
            line = map_file.readline()

    def _move_unit(self, unit, new_pos):
        """
        Moves a unit within the directory.
        NOTE: This does not change the unit's screen position!
        """
        old_pos = self.map.tile_coords((unit.rect.x, unit.rect.y))
        
        # Remove it from the old position
        self._unit_directory[old_pos] = None
        self._unit_directory[new_pos] = unit
        
    def on_click(self, e):
        """
        This is called when a click event occurs.
        e is the click event.
        """
        # make sure we have focus and that it was the left mouse button
        if (e.type == pygame.MOUSEBUTTONUP
            and e.button == 1
            and pygame.mouse.get_focused()):
            
            # If this is in the map, we're dealing with units
            if self.map.rect.collidepoint(e.pos):
                # get the unit at the mouseclick
                unit = self.unit_at_screen_pos(e.pos)

                #TODO, this will need to be updated once we have a concept of ownership
                # as well as attack/move states

                # clicking the same unit again deselects it
                if unit == self.sel_unit:
                    self.sel_unit = None
                    self.map.clear_highlights()

                # update the selected unit
                elif unit and unit != self.sel_unit:
                    self.sel_unit = unit
                    self.map.clear_highlights()
            
            # Otherwise, the user is interacting with the GUI panel
            else:
                # Check which button was pressed
                for button in self.buttons:
                    if self.get_button_rect(button).collidepoint(e.pos):
                        button.onClick()
                        
    def unit_at_pos(self, pos):
        """
        Gets the unit at a specified tile position ((x,y) tuple).
        Returns None if no unit.
        """
        return self._unit_directory[pos]
                
    def unit_at_screen_pos(self, pos):
        """
        Gets the unit at a specified screen position ((x,y) tuple).
        Returns None if no unit.
        """
        # Get the unit's tile position.
        tile_pos = self.map.tile_coords(pos)
        return self.unit_at_pos(tile_pos)

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
        self.draw_bar()

        # Update the screen
        pygame.display.flip()

    def draw_bar(self):
        """
        Draws the info bar on the right side of the screen, polls the mouse
        location to find which tile is currently being hovered over.
        """
        if not self.map: return
        
        line_num = 0
        #draw the background of the bar
        barRect = pygame.Rect(MAP_WIDTH, 0, BAR_WIDTH,
            self.screen.get_height())
        outlineRect = pygame.Rect(MAP_WIDTH, 0, BAR_WIDTH - 1,
            self.screen.get_height() - 1)
        pygame.draw.rect(self.screen, BAR_COLOR, barRect)
        pygame.draw.rect(self.screen, OUTLINE_COLOR, outlineRect, 2)

        #title for tile section
        self.draw_bar_title("TILE INFO", line_num)
        line_num += 1
        
        #Tile coordinates
        mouse_pos = pygame.mouse.get_pos()
        coords = self.map.tile_coords(mouse_pos)
        self.draw_bar_text("Coordinates: {}".format(coords), line_num)
        line_num += 1

        #Is the tile passable?
        #We can only know if there's a unit currently selected
        if self.sel_unit:
            tile = self.map.tile_data(coords)
            self.draw_bar_text(
                "Passable: {}".format(self.sel_unit.is_passable(tile)),
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

        for button in self.buttons:
            self.draw_bar_button(button)

    def draw_bar_text(self, text, line_num):
        """
        Draws text with a specified variable at a specifed line number.
        """
        line_text = self.font.render(text, True, FONT_COLOR)
        self.screen.blit(
            line_text,
            (MAP_WIDTH + PAD, FONT_SIZE * line_num + PAD))

    def draw_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = self.font.render(text, True, FONT_COLOR)
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
            
    def get_button_rect(self, button):
        """
        Gets the rectangle bounding a button in screen cordinates.
        """
        # The y-coordinate is based on its slot number
        y = self.screen.get_height() - BUTTON_HEIGHT * (button.slot + 1)
        return pygame.Rect(MAP_WIDTH, y, BAR_WIDTH, BUTTON_HEIGHT)

    def draw_bar_button(self, button):
        """
        Renders a button to the bar.
        If the mouse is hovering over the button it is rendered in white, else
        rgb(50, 50, 50).
        """

        but_rect = self.get_button_rect(button)
        
        # The outline needs a slightly smaller rectangle
        but_out_rect = but_rect
        but_out_rect.width -= 1

        # Highlight on mouse over
        mouse_pos = pygame.mouse.get_pos()
        if but_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, but_rect)
        else:
            pygame.draw.rect(self.screen, BAR_COLOR, but_rect)
            
        # Draw the outline
        pygame.draw.rect(self.screen, OUTLINE_COLOR, but_out_rect, 2)

        # Draw the text
        but_text = self.font.render(button.text, True, FONT_COLOR)
        self.screen.blit(
            but_text,
            (MAP_WIDTH + CENTER - (but_text.get_width()/2),
            but_rect.y + (BUTTON_HEIGHT//2) - but_text.get_height()//2))
