import sys, pygame
from pygame.sprite import LayeredUpdates
from collections import namedtuple
import tiles, unit, animation
from unit import *
from effects.explosion import Explosion

MAP_WIDTH = 600
BAR_WIDTH = 200
BUTTON_HEIGHT = 50
CENTER = 100

# Set the fonts
pygame.font.init()
FONT_SIZE = 16
BIG_FONT_SIZE = 42
FONT = pygame.font.SysFont("Arial", FONT_SIZE)
BIG_FONT = pygame.font.SysFont("Arial", BIG_FONT_SIZE)
BIG_FONT.set_bold(True)

# padding for left and top side of the bar
PAD = 6

# Speed of reticle blinking
RETICLE_RATE = 0.02

# RGBA colors for grid stuff
SELECT_COLOR = (255, 255, 0, 255)
MOVE_COLOR_A = (0, 0, 210, 80)
MOVE_COLOR_B = (75, 125, 255, 120)
ATK_COLOR_A = (255, 0, 0, 140)
ATK_COLOR_B = (255, 125, 75, 180)

# RGB colors for the GUI
FONT_COLOR = (0, 0, 0)
BAR_COLOR = (150, 150, 150)
OUTLINE_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (255, 255, 255)

# Names for the different teams
TEAM_NAME = {
    0: "green",
    1: "red"
}

# Possible GUI modes
# http://stackoverflow.com/questions/702834/whats-the-common-practice-for-enums-
# in-python
class Modes:
    Select, ChooseMove, Moving, ChooseAttack, GameOver = range(5)

# A container class which stores button information.
# Each "slot" is a BUTTON_HEIGHT pixel space counting up from the bottom
# of the screen.
Button = namedtuple('Button', ['slot', 'text', 'onClick'])

class GUI(LayeredUpdates):
    """
    This class handles user input, and is also responsible for rendering objects
    on-screen (including converting unit tile positions into on-screen
    positions). Essentially, it is the middleman between objects and the actual
    tilemap.
    """
    # number of GUI instances
    num_instances = 0
            
    def move_pressed(self):
        """
        This is called when the move button is pressed.
        """
        # Switch out of move mode if we're already in it.
        if self.mode == Modes.ChooseMove:
            self.change_mode(Modes.Select)
            return
        
        # If there is no unit selected, nothing happens.
        if not self.sel_unit: return
        # If the unit has already moved nothing happens.
        elif self.sel_unit.turn_state[0] == True: return
        
        # Determine where we can move.
        pos = (self.sel_unit.tile_x, self.sel_unit.tile_y)
        
        self._movable_tiles = tiles.reachable_tiles(
            self.map,
            pos,
            self.sel_unit.speed,
            self.sel_unit.move_cost,
            self.sel_unit.is_passable)
        
        # We can't actually move to any tiles with units in them
        for u in base_unit.BaseUnit.active_units:
            u_pos = (u.tile_x, u.tile_y)
            if u_pos in self._movable_tiles:
                self._movable_tiles.remove(u_pos)
        
        # Highlight those squares
        self.map.set_highlight(
            "move", MOVE_COLOR_A, MOVE_COLOR_B, self._movable_tiles)
        
        # Set the current GUI mode
        self.change_mode(Modes.ChooseMove)
            
    def attack_pressed(self):
        """
        This is called when the attack button is pressed.
        """
        # Switch out of move mode if we're already in it.
        if self.mode == Modes.ChooseAttack:
            self.change_mode(Modes.Select)
            return
        
        # If there is no unit selected, nothing happens.
        if not self.sel_unit: return
        # If the unit has already attacked, nothing happens.
        elif self.sel_unit.turn_state[1] == True: return
        
        # Get information about the unit and its location.
        unit_pos = (self.sel_unit.tile_x, self.sel_unit.tile_y)
        unit_tile = self.map.tile_data(unit_pos)
        
        # These are all the tiles in range of the unit's attack.
        in_range = self.sel_unit.tiles_in_range(unit_tile, unit_pos)
        
        # Determine which tiles the unit can actually attack.
        for check_pos in in_range:
            check_tile = self.map.tile_data(check_pos)
            if self.sel_unit.is_attackable(
                unit_tile,
                unit_pos,
                check_tile,
                check_pos):
                self._attackable_tiles.add(check_pos)
        
        # Highlight the attackable tiles
        self.map.set_highlight(
            "attack", ATK_COLOR_A, ATK_COLOR_B, in_range)
            
        # Reset the reticle blinking
        self._reticle.reset()
        
        # Set the current GUI mode
        self.change_mode(Modes.ChooseAttack)
        
    def end_turn_pressed(self):
        """
        This is called when the end turn button is pressed.
        Advances to the next turn.
        """
        # advance turn
        self.current_turn += 1
        
        # reset game mode
        self.change_mode(Modes.Select)
        
        # unselect unit
        self.sel_unit = None
        
        # Reset the turn states of all units
        for unit in base_unit.BaseUnit.active_units:
            if unit.team == self.get_cur_team():
                unit.turn_state = [False, False]

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

        # Set up team information
        self.num_teams = None
        self.current_turn = 0
        self.win_team = None 

        # The currently selected unit
        self.sel_unit = None
        
        # Set up GUI
        self.buttons = [
            Button(0, "MOVE", self.move_pressed),
            Button(1, "ATTACK", self.attack_pressed),
            Button(2, "END TURN", self.end_turn_pressed)]
        
        # We start in select mode
        self.mode = Modes.Select
        
        # Tiles we can move to/attack
        self._movable_tiles = set()
        self._attackable_tiles = set()

        # The targeting reticle
        self._reticle = animation.Animation("assets/reticle.png",
                                             20,
                                             20,
                                             RETICLE_RATE)
        
        # This will store effects which are drawn over everything else
        self._effects = pygame.sprite.Group()
        
    def get_cur_team(self):
        """
        Gets the current team based on the turn.
        """
        return (self.current_turn) % self.num_teams
        
    def get_cur_day(self):
        """
        Gets the current day based on the turn.
        """
        return (self.current_turn) // self.num_teams + 1
        
    def change_mode(self, new_mode):
        """
        Changes the current mode.
        """
        if self.mode == new_mode:
            return
        
        # Deal with the current mode
        if self.mode == Modes.ChooseMove:
            # Reset the move markers
            self._movable_tiles = set()
            self.map.remove_highlight("move")
        
        # Deal with the current mode
        if self.mode == Modes.ChooseAttack:
            # Reset the move markers
            self._attackable_tiles = set()
            self.map.remove_highlight("attack")
            
        self.mode = new_mode
        
    def load_level(self, filename):
        """
        Loads a map from the given filename.
        """
        self.remove(self.map)
        
        map_file = open(filename, 'r')
        
        # Get the map size
        line = map_file.readline()
        w, h = [int(x) for x in line.split('x')]
        
        # Get the number of teams
        line = map_file.readline()
        self.num_teams = int(line)
        
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
        self.map.set_tiles(map_tiles)
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
            unit_team = int(line[1])
            unit_x, unit_y = int(line[2]), int(line[3])
            unit_angle = int(line[4])
            
            if not unit_name in unit.unit_types:
                raise Exception("No unit of name {} found!".format(unit_name))
            new_unit = unit.unit_types[unit_name](team = unit_team,
                                                  tile_x = unit_x,
                                                  tile_y = unit_y,
                                                  activate = True,
                                                  angle = unit_angle)
            
            # Add the unit to the update group and set its display rect
            self.update_unit_rect(new_unit)
            
            line = map_file.readline()
        
    def on_click(self, e):
        """
        This is called when a click event occurs.
        e is the click event.
        """
        # Don't react when in move, attack or game over mode.
        if (self.mode == Modes.Moving or
            self.mode == Modes.GameOver):
            return
        
        # make sure we have focus and that it was the left mouse button
        if (e.type == pygame.MOUSEBUTTONUP
            and e.button == 1
            and pygame.mouse.get_focused()):
            
            # If this is in the map, we're dealing with units or tiles
            if self.map.rect.collidepoint(e.pos):
                # Get the tile's position
                to_tile_pos = self.map.tile_coords(e.pos)

                # get the unit at the mouseclick
                unit = self.unit_at_screen_pos(e.pos)
                
                if unit:
                    # clicking the same unit again deselects it and, if
                    # necessary, resets select mode
                    if unit == self.sel_unit:
                        self.change_mode(Modes.Select)
                        self.sel_unit = None

                    # select a new unit
                    elif (self.mode == Modes.Select and
                          unit.team == self.get_cur_team()):
                        self.sel_unit = unit
                    elif (self.mode == Modes.ChooseAttack and
                        self.sel_unit and
                        to_tile_pos in self._attackable_tiles):
                        # Attack the selected tile
                        self.sel_unit_attack(to_tile_pos)
                else:
                    # No unit there, so a tile was clicked
                    if (self.mode == Modes.ChooseMove and
                        self.sel_unit and
                        to_tile_pos in self._movable_tiles):
                        
                        # Move to the selected tile
                        self.sel_unit_move(to_tile_pos)
            
            # Otherwise, the user is interacting with the GUI panel
            else:
                # Check which button was pressed
                for button in self.buttons:
                    if self.get_button_rect(button).collidepoint(e.pos):
                        button.onClick()
                        
    def sel_unit_attack(self, pos):
        """
        Attack the given position using the selected unit.
        """
        # Change the game state to show that there was an attack.
        self.change_mode(Modes.Select)
        
        # Mark that the unit has attacked.
        self.sel_unit.turn_state[1] = True
        
        # Face the attackee
        self.sel_unit.face_vector((
            pos[0] - self.sel_unit.tile_x,
            pos[1] - self.sel_unit.tile_y))
        
        # Get info about the attackee
        atk_unit = self.unit_at_pos(pos)
        atk_tile = self.map.tile_data(pos)
        
        # Calculate the damage
        damage = self.sel_unit.get_damage(atk_unit) - atk_tile.defense
        
        # Deal damage
        atk_unit.hurt(damage)
        
        # Explode
        self._effects.add(Explosion(self.map.screen_coords(pos)))
        
        # If the unit was destroyed, check if there are any others left on a
        # team other than the selected unit
        for u in unit.base_unit.BaseUnit.active_units:
            if u.team != self.sel_unit.team:
                return
                
        # No other units, so game over!
        self.win_team = self.sel_unit.team
        self.mode = Modes.GameOver
    
    def sel_unit_move(self, pos):
        """
        Move the selected unit to the given position.
        """
        # Change the game state to show that there was a movement.
        self.change_mode(Modes.Moving)
        
        # Mark that the unit has moved
        self.sel_unit.turn_state[0] = True
        
        #the tile position the unit is at
        from_tile_pos = (self.sel_unit.tile_x,
                         self.sel_unit.tile_y)
        
        #set the path in the unit.
        self.sel_unit.set_path(
            tiles.find_path(
                self.map,
                from_tile_pos,
                pos,
                self.sel_unit.move_cost,
                self.sel_unit.is_passable))
                        
    def unit_at_pos(self, pos):
        """
        Gets the unit at a specified tile position ((x,y) tuple).
        Returns None if no unit.
        """
        for u in base_unit.BaseUnit.active_units:
            
            #the postion of the unit in tile coords
            unit_pos = (u.tile_x, u.tile_y)
            
            #compare to the desired coord
            if unit_pos == pos:
                return u
                
        return None
                
    def unit_at_screen_pos(self, pos):
        """
        Gets the unit at a specified screen position ((x,y) tuple).
        Returns None if no unit.
        """
        # Get the unit's tile position.
        tile_pos = self.map.tile_coords(pos)
        return self.unit_at_pos(tile_pos)
        
    def update_unit_rect(self, unit):
        """
        Scales a unit's display rectangle to screen coordiantes.
        """
        x, y = unit.tile_x, unit.tile_y
        screen_x, screen_y = self.map.screen_coords((x, y))
        unit.rect.x = screen_x
        unit.rect.y = screen_y
        
    def update(self):
        """
        Update everything in the group.
        """
        LayeredUpdates.update(self)
        
        # Update units
        base_unit.BaseUnit.active_units.update()
        
        # The unit is finished moving, so go back to select
        if self.mode == Modes.Moving:
            if (not self.sel_unit) or (not self.sel_unit.is_moving()):
                self.change_mode(Modes.Select)
                
        # Update the reticle effect
        self._reticle.update()
        
        # Update effects
        self._effects.update()

    def draw(self):
        """
        Render the display.
        """
        # Fill in the background
        self.screen.fill(self.bg_color)
        
        # Update and draw the group contents
        LayeredUpdates.draw(self, self.screen)
        
        # draw units
        for unit in base_unit.BaseUnit.active_units:
            self.update_unit_rect(unit)
        base_unit.BaseUnit.active_units.draw(self.screen)
        
        # If there's a selected unit, outline it
        if self.sel_unit:
            pygame.gfxdraw.rectangle(
                self.screen,
                self.sel_unit.rect,
                SELECT_COLOR)
                
        # Mark potential targets
        for tile_pos in self._attackable_tiles:
            screen_pos = self.map.screen_coords(tile_pos)
            self.draw_reticle(screen_pos)
            
        # Draw effects
        self._effects.draw(self.screen)
        
        # Draw the status bar
        self.draw_bar()
        
        # Draw the win message
        if self.mode == Modes.GameOver:
            # Determine the message
            win_text = "TEAM {} WINS!".format(
                TEAM_NAME[self.win_team].upper())
            
            # Render the text
            win_msg = BIG_FONT.render(
                win_text,
                True,
                FONT_COLOR)
                
            # Move it into position
            msg_rect = pygame.Rect((0, 0), win_msg.get_size())
            msg_rect.center = (MAP_WIDTH / 2, self.screen.get_height() / 2)
            
            # Draw it
            self.screen.blit(win_msg, msg_rect)

        # Update the screen
        pygame.display.flip()
        
    def draw_reticle(self, pos):
        """
        Draws a reticle with its top-left corner at pos.
        """
        self.screen.blit(self._reticle.image, pos)

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
        
        #Title for turn info
        self.draw_bar_title("DAY {}".format(self.get_cur_day()), line_num)
        line_num += 1
        
        self.draw_bar_title(
            "TEAM {}'S TURN".format(
                TEAM_NAME[self.get_cur_team()].upper()),
            line_num)
        line_num += 1
        
        #divider
        self.draw_bar_div_line(line_num)
        line_num += 1

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
                "Passable: {}".format(self.sel_unit.is_passable(
                    tile, coords)),
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
        line_text = FONT.render(text, True, FONT_COLOR)
        self.screen.blit(
            line_text,
            (MAP_WIDTH + PAD, FONT_SIZE * line_num + PAD))

    def draw_bar_title(self, text, line_num):
        """
        Draws a title at a specified line number with the specified text.
        """
        title_text = FONT.render(text, True, FONT_COLOR)
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
        but_text = FONT.render(button.text, True, FONT_COLOR)
        self.screen.blit(
            but_text,
            (MAP_WIDTH + CENTER - (but_text.get_width()/2),
            but_rect.y + (BUTTON_HEIGHT//2) - but_text.get_height()//2))
