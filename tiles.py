import pygame, sys, math
import pygame.gfxdraw
import pqueue
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

def manhattan_dist(a, b):
    """
    Returns the Manhattan distance between two points.
    
    >>> manhattan_dist((0, 0), (5, 5))
    10
    >>> manhattan_dist((0, 5), (10, 7))
    12
    >>> manhattan_dist((12, 9), (2, 3))
    16
    """
    return abs(a[0] - b[0] + a[1] - b[1])

def squared_dist(a, b):
    """
    Returns the squared distance "as the crow flies" between two points.
    
    >>> squared_dist((0, 0), (5, 5)) == 50
    True
    >>> squared_dist((0, 5), (10, 7)) == 104
    True
    >>> squared_dist((12, 9), (2, 3)) == 136
    True
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    return dx * dx + dy * dy    
    
def squared_segment_dist(p, a, b):
    """
    Returns the distance between a point p and a line segment between
    the points a and b.
    Code adapted from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    """
    len2 = squared_dist(a, b)
    # If the segment is actually a point, our job is a lot easier!
    if len2 == 0: return squared_dist(p, a)
    # Our line is a + t * (b - a)
    # The t at which p is closest is when the vector (a, p) is projected
    # onto the vector (a, b) (dot product)
    t = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / len2
    if t < 0: return squared_dist(p, a) # Beyond point a
    if t > 1: return squared_dist(p, b) # Beyond point b
    close_point = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )
    return squared_dist(p, close_point)
    
def compare_tile(a, b, start, end):
    """
    Picks the best tile to use. This is used in case of a tie in the
    priority queue. Returns True if choosing tile a, or False for tile b.
    The tile with the closest slope to the slope between start and end
    will be given priority. If there's still a tie, the tile with the
    lowest Y is chosen. Finally, if that fails, the tile with the lowest
    X is chosen.
    """
    dist_a = round(squared_segment_dist(a, start, end), 3)
    dist_b = round(squared_segment_dist(b, start, end), 3)
    
    # Choose the lowest slope difference
    if dist_a < dist_b:
        return True
    elif dist_a > dist_b:
        return False
    else:
        # Still a tie - choose lowest Y
        if a[1] < b[1]:
            return True
        elif a[1] > b[1]:
            return False
        else:
            # Still a tie - choose lowest X
            if a[0] < b[0]:
                return True
            else:
                return False

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
        self._sprite_sheet = pygame.image.load(sheet_name)
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._map_width = map_width
        self._map_height = map_height
        self._tiles = []
        self._highlights = {}
        self._grid_color = (0, 0, 0, 64)
        
        # Fill the list with empty tiles
        for i in range(self._tile_count()):
            self._tiles.append(0)
        
        Sprite.__init__(self)
        
        # These are required for a pygame Sprite
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
        
    def _tile_exists(self, coords):
        """
        Returns true if a tile exists, or false if it doesn't
        """
        return not (coords[0] < 0 or coords[0] >= self._map_width or coords[1] < 0 or coords[1] >= self._map_height)
        
    def _tile_index(self, coords):
        """
        Returns a tile's index in the list given its tile coordinates in tile units.
        Returns -1 if the provided coordinates are invalid
        """
        if not self._tile_exists(coords): return -1
        
        return coords[1] * self._map_width + coords[0]
        
    def tile_coords(self, screen_coords):
        """
        Returns the tile coordinates within this TileMap that the given screen coordinates fall into.
        """
        x, y = screen_coords
        return (
            math.floor((x - self.rect.left) / self._tile_width),
            math.floor((y - self.rect.top) / self._tile_height)
        )
        
    def is_passable(self, coords):
        """
        Returns true if a given tile index is passable, and false otherwise.
        """
        if not self._tile_exists(coords): return False
        
        index = self._tile_index(coords)
        
        return tile_types[self._tiles[index]].passable
        
    def set_highlight(self, colour, tiles):
        """
        Sets the given list of tile coordinates to be highlighted in colour.
        """
        self._highlights[colour] = tiles
        
    def remove_highlight(self, colour):
        """
        Removes highlights of the given colour. If the highlights do not
        exist, does nothing.
        """
        if colour in self._highlights:
            del self._highlights[colour]
        
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
        
            
        # draw the highlights
        for colour, tiles in self._highlights.items():
            for coord in tiles:
                tile_rect = pygame.Rect(
                    coord[0] * self._tile_width,
                    coord[1] * self._tile_height,
                    self._tile_width,
                    self._tile_height
                )
                pygame.gfxdraw.box(self.image, tile_rect, colour)
            
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
        
    def find_path(self, start, end, cost = lambda x: 1):
        """
        Returns the path between two points as a list of tile coordinates using the A* algorithm.
        If no path could be found, an empty list is returned.
        
        Code based on algorithm described in http://www.policyalmanac.org/games/aStarTutorial.htm
        """
        # tiles to check (tuples of x, y)
        todo = pqueue.PQueue()
        todo.update(start, 0)
        
        # tiles we've been to
        visited = set()
        
        # associated G and H costs for each tile (tuples of G, H)
        costs = {}
        
        # parents for each tile
        parents = {}
        
        while todo and (end not in visited):
            todo.tie_breaker = lambda a,b: compare_tile(a, b, start, end)
        
            cur, c = todo.pop_smallest()
            x, y = cur
            visited.add(cur)
            
            # check neighbours
            neighbours = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            ]
            for n in neighbours:
                # skip it if it doesn't exist, if we've already checked it, or if it isn't passable
                if (not self._tile_exists(n)) or (n in visited) or (not self.is_passable(n)): continue
                
                # we haven't looked at this tile yet, so calculate its costs
                if n not in todo:
                    g, h = c + cost(cur), manhattan_dist(n, end)
                    costs[n] = (g, h)
                    parents[n] = cur
                    todo.update(n, g + h)
                else:
                    # if we've found a better path, update it
                    g, h = costs[n]
                    if c + cost(cur) < g:
                        g = c + cost(cur)
                        todo.update(n, g + h)
                        costs[n] = (g, h)
                        parents[n] = cur
        
        if end not in visited:
            return []
        
        # build the path backward
        path = []
        while end != start:
            path.append(end)
            end = parents[end]
        path.append(start)
        path.reverse()
        
        return path
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
