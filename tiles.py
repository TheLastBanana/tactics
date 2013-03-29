import pygame, sys
import pygame.gfxdraw
from pygame.sprite import Sprite
from collections import namedtuple

# A container class which stores information about a tile.
Tile = namedtuple('Tile', ['sprite_id', 'passable'])

# a dictionary of tile IDs associated with their type data
tile_types = {
    0:  Tile(0, True),       # default
    1:  Tile(1, False),      # wall
    2:  Tile(2, False)       # water
}

class TileMap(Sprite):
    """
    A class which renders a grid of tiles from a spritesheet.
    """
    def __init__(self, target, sheet_name, tile_width, tile_height, map_width, map_height):
        """
        target: the render target
        sheet_name: the filename of the sprite sheet to use
        tile_width: the width of each tile, in pixels
        tile_height: the height of each tile, in pixels
        map_width: the width of map, in tiles
        map_height: the height of the map, in tiles
        """
        import random
        
        self.test_path = self.find_path((0, 0), (10, 10))
        
        self._sprite_sheet = pygame.image.load(sheet_name)
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._map_width = map_width
        self._map_height = map_height
        self._tiles = []
        self._grid_color = (0, 0, 0, 64)
        for i in range(self._tile_count()):
            self._tiles.append(0)
        
        Sprite.__init__(self)
        
        self.image = pygame.Surface((self._tile_width * self._map_width, self._tile_height * self._map_height))
        self.rect = self.image.get_rect()
        
    def _tile_count(self):
        """
        Returns the number of tiles on the map.
        """
        return self._map_width * self._map_height
        
    def _tile_position(self, index):
        """
        Returns a tile's coordinates in tile units within the map given its index in the list.
        """
        return (index % self._map_width, index // self._map_height)
        
    def _tile_index(self, coords):
        """
        Returns a tile's index in the list given its tile coordinates in tile units.
        """
        return coords[1] * self._map_width + coords[0]
        
    def update(self):
        """
        Overrides the default update function for sprites. This updates the image.
        """
        # clear the image
        self.image.fill((0, 0, 0, 0))
        
        # draw in each tile
        for i in range(self._tile_count()):
            tile_id = tile_types[self._tiles[i]].sprite_id
            
            # get its position from its index in the list
            x, y = self._tile_position(i)
            x *= self._tile_width
            y *= self._tile_height
            
            # determine which subsection to draw based on the sprite id
            area = pygame.Rect(tile_id * self._tile_width, 0, self._tile_width, self._tile_height)
            
            # draw the tile
            self.image.blit(self._sprite_sheet, (x, y), area)
            
        # draw the grid
        for x in range(0, self._map_width * self._tile_width, self._tile_width):
            pygame.gfxdraw.vline(self.image, x, 0, self._map_height * self._tile_height, self._grid_color)
        for y in range(0, self._map_height * self._tile_height, self._tile_height):
            pygame.gfxdraw.hline(self.image, 0, self._map_width * self._tile_width, y, self._grid_color)
                
            
        # draw the debug path
        for c in self.test_path:
            tile_rect = pygame.Rect(c[0] * self._tile_width, c[1] * self._tile_height, self._tile_width, self._tile_height)
            pygame.gfxdraw.box(self.image, tile_rect, (255, 0, 0, 150))
            
    def load_from_file(self, filename):
        """
        Loads tile data in from a given file.
        The file should be space-separated.
        """
        tile_file = open(filename, 'r')
        
        lines = tile_file.readlines()
        if len(lines) < self._map_height:
                raise Exception("Expected {} rows of tiles, but got {}".format(self._map_height, len(lines)))
        
        # this will store the new set of tiles temporarily so that we can revert in case the read operation fails
        new_tiles = []
        
        for line in lines:
            line = line.rstrip()
            line = line.split(' ')
            
            # there should be map_width tiles per line
            if len(line) < self._map_width:
                raise Exception("Expected {} tiles per line, but got {}".format(self._map_width, len(line)))
            
            # add all the tiles
            for c in line:
                new_tiles.append(int(c))
                
        tile_file.close()
        
        # we loaded in the file properly, so copy it over to tiles
        self._tiles = new_tiles[:]
        
    def find_path(self, start, end):
        """
        Returns the path between two points as a list of tile coordinates using the A* algorithm.
        """
        return [start, end]
