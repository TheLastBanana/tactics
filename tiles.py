import pygame, sys
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
        
        self._sprite_sheet = pygame.image.load(sheet_name)
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._map_width = map_width
        self._map_height = map_height
        self._tiles = []
        for i in range(self._tile_count()):
            self._tiles.append(0)
        
        Sprite.__init__(self)
        
        self.image = pygame.Surface((self._tile_width * self._map_width, self._tile_height * self._map_height))
        self.rect = self.image.get_rect()
        
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
            x = (i % self._map_width) * self._tile_width
            y = (i // self._map_height) * self._tile_height
            
            # determine which subsection to draw based on the sprite id
            area = pygame.Rect(tile_id * self._tile_width, 0, self._tile_width, self._tile_height)
            
            # draw the ti.e
            self.image.blit(self._sprite_sheet, (x, y), area)
            
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
        
    def _tile_count(self):
        """
        Returns the number of tiles on the map.
        """
        return self._map_width * self._map_height
