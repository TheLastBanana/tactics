import pygame, sys, math
import pygame.gfxdraw
import pqueue, helper
from pygame.sprite import Sprite
from collections import namedtuple

# A container class which stores information about a tile.
Tile = namedtuple('Tile', ['type', 'sprite_id', 'passable'])

# a dictionary of tile IDs associated with their type data
tile_types = {
    0:  Tile('plains', 0, True),
    1:  Tile('wall', 1, False),
    2:  Tile('water', 2, False)
}

HIGHLIGHT_RATE = 0.0025
    
def better_tile(a, b, start, end):
    """
    Picks the best tile to use. This is used in case of a tie in the
    priority queue. Returns True if choosing tile a, or False for tile b.
    The tile with the closest slope to the slope between start and end
    will be given priority. If there's still a tie, the tile with the
    lowest Y is chosen. Finally, if that fails, the tile with the lowest
    X is chosen.
    
    Examples:
    The best tile here is (1, 1), as it lies directly on the line:
    >>> better_tile((1, 1), (1, 2), (0, 0), (3, 3))
    True
    
    The best tile here is (1, 4), as it lies closer to the line:
    >>> better_tile((1, 1), (1, 4), (0, 3), (3, 3))
    False
    
    Both tiles are equidistant to the line, so we choose the lowest Y,
    (1, 0):
    >>> better_tile((0, 1), (1, 0), (0, 0), (3, 3))
    False
    
    Both tiles are equidistant to the line and have equal Y, so we
    choose the lowest X, (3, 1):
    >>> better_tile((3, 1), (5, 1), (4, 0), (4, 4))
    True
    """
    dist_a = round(helper.squared_segment_dist(a, start, end), 3)
    dist_b = round(helper.squared_segment_dist(b, start, end), 3)
    
    # Choose the lowest difference from the line
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
    
    def __init__(self, sheet_name, tile_width, tile_height,
        map_width, map_height):
        """
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
        self.tiles = []
        self._highlights = {}
        self._grid_color = (0, 0, 0, 64)
        
        # Fill the list with empty tiles
        for i in range(self._tile_count()):
            self.tiles.append(0)
        
        Sprite.__init__(self)
        
        # These are required for a pygame Sprite
        self.image = pygame.Surface(
            (self._tile_width * self._map_width,
            self._tile_height * self._map_height)
        )
        self.rect = self.image.get_rect()
        
    def _tile_count(self):
        """
        Returns the number of tiles on the map.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t._tile_count()
        25
        """
        return self._map_width * self._map_height
        
    def _tile_position(self, index):
        """
        Returns a tile's coordinates in tile units within the map given its
        index in the list.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t._tile_position(12)
        (2, 2)
        """
        return (index % self._map_width, index // self._map_width)
        
    def _tile_exists(self, coords):
        """
        Returns true if a tile exists, or false if it doesn't
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t._tile_exists((2, 2))
        True
        >>> t._tile_exists((-2, -1))
        False
        >>> t._tile_exists((6, 7))
        False
        """
        return not (
            coords[0] < 0 or
            coords[0] >= self._map_width or
            coords[1] < 0 or
            coords[1] >= self._map_height)
        
    def _tile_index(self, coords):
        """
        Returns a tile's index in the list given its tile coordinates in tile
        units. Returns -1 if the provided coordinates are invalid.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t._tile_index((2, 2))
        12
        """
        if not self._tile_exists(coords): return -1

        #make sure to cast to int because input is sometimes floats
        #There won't be rounding errors though because the numbers
        #are just integers with .0 after
        return int(coords[1]) * self._map_width + int(coords[0])
        
    def tile_coords(self, screen_coords):
        """
        Returns the tile coordinates within this TileMap that the given screen
        coordinates fall into.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t.tile_coords((45, 22))
        (2, 1)
        """
        x, y = screen_coords
        return (
            math.floor((x - self.rect.left) / self._tile_width),
            math.floor((y - self.rect.top) / self._tile_height)
        )
        
    def screen_coords(self, tile_coords):
        """
        Returns the screen coordinates of a given tile.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
        >>> t.screen_coords((3, 4))
        (60, 80)
        """
        x, y = tile_coords
        return (
            x * self._tile_width,
            y * self._tile_height
        )
        
    def tile_data(self, coords):
        """
        Returns the tile data for a given tile.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 2, 2)
        >>> t.tiles = [0, 0,\
                       0, 1]
        >>> t.tile_data((0, 0)) == tile_types[0]
        True
        >>> t.tile_data((1, 1)) == tile_types[1]
        True
        
        """
        if not self._tile_exists(coords): return False
        
        index = self._tile_index(coords)
        
        return tile_types[self.tiles[index]]
        
    def tile_neighbours(self, coords):
        """
        Returns all neighbour coordinates to a given tile. Does not return
        coordinates which do not exist.
        
        >>> t = TileMap("assets/tiles.png", 20, 20, 3, 3)
        >>> t.tiles = [0, 0, 0,\
                       0, 0, 0,\
                       0, 0, 0]
        >>> t.tile_neighbours((0, 0))
        [(1, 0), (0, 1)]
        >>> t.tile_neighbours((2, 2))
        [(2, 1), (1, 2)]
        >>> t.tile_neighbours((1, 1))
        [(1, 0), (2, 1), (0, 1), (1, 2)]
        """
        x, y = coords
        
        # The possible neighbouring tiles.
        neighbours = [
            (x, y - 1),
            (x + 1, y),
            (x - 1, y),
            (x, y + 1)
        ]
        
        # Return only those which exist.
        return [n for n in neighbours if self._tile_exists(n)]
        
    def set_highlight(self, name, colorA, colorB, tiles):
        """
        Sets the given list of tile coordinates to be highlighted in the given
        color and wave between the first and second colors.
        It will be stored under the given name.
        """
        self._highlights[name] = (tiles, colorA, colorB)
        
    def remove_highlight(self, name):
        """
        Removes highlights of the given colour. If the highlights do not
        exist, does nothing.
        """
        if name in self._highlights:
            del self._highlights[name]
            
    def clear_highlights(self):
        """
        Removes all highlights.
        """
        self._highlights.clear()
        
    def _get_highlight_color(self, colorA, colorB):
        """
        Returns the movement color, which changes based on time.
        """
        # This produces a sine wave effect between a and b.
        sin = (math.sin(pygame.time.get_ticks() * HIGHLIGHT_RATE) + 1) * 0.5
        effect = lambda a, b: a + sin * (b - a)
        
        r = effect(colorA[0], colorB[0])
        g = effect(colorA[1], colorB[1])
        b = effect(colorA[2], colorB[2])
        a = effect(colorA[3], colorB[3])
        
        return (r, g, b, a)
        
    def update(self):
        """
        Overrides the default update function for sprites. This updates
        the image.
        """
        # clear the image
        self.image.fill((0, 0, 0, 0))
        
        # draw in each tile
        for i in range(self._tile_count()):
            tile_id = tile_types[self.tiles[i]].sprite_id
            
            # get its position from its index in the list
            x, y = self._tile_position(i)
            x *= self._tile_width
            y *= self._tile_height
            
            # determine which subsection to draw based on the sprite id
            area = pygame.Rect(
                tile_id * self._tile_width,
                0,
                self._tile_width,
                self._tile_height
            )
            
            # draw the tile
            self.image.blit(self._sprite_sheet, (x, y), area)
            
        # draw the highlights
        for name, (tiles, colorA, colorB) in self._highlights.items():
            for coord in tiles:
                tile_rect = pygame.Rect(
                    coord[0] * self._tile_width,
                    coord[1] * self._tile_height,
                    self._tile_width,
                    self._tile_height
                )
                pygame.gfxdraw.box(self.image,
                                   tile_rect,
                                   self._get_highlight_color(colorA, colorB))
            
        # draw the grid
        for x in range(0, self._map_width * self._tile_width, self._tile_width):
            pygame.gfxdraw.vline(
                self.image,
                x,
                0,
                self._map_height * self._tile_height,
                self._grid_color
            )
        for y in range(0, self._map_height * self._tile_height, self._tile_height):
            pygame.gfxdraw.hline(
                self.image,
                0,
                self._map_width * self._tile_width,
                y,
                self._grid_color
            )
            
def find_path(tilemap,
                start,
                end,
                cost = lambda tile: 1,
                passable = lambda tile, pos: tile.passable):
    """
    Returns the path between two points as a list of tile coordinates using
    the A* algorithm.
    If no path could be found, an empty list is returned.
    
    Code based on algorithm described in:
    http://www.policyalmanac.org/games/aStarTutorial.htm
    
    Example use:
    >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
    >>> t.tiles = [0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0]
    
    >>> find_path(t, (0, 0), (4, 4))
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4)]
    >>> find_path(t, (0, 0), (5, 5))
    []
    
    >>> t = TileMap("assets/tiles.png", 20, 20, 6, 6)
    >>> t.tiles = [0, 0, 0, 0, 1, 0,\
                   0, 1, 1, 1, 0, 0,\
                   0, 0, 0, 0, 1, 0,\
                   0, 1, 1, 0, 1, 0,\
                   0, 0, 1, 0, 0, 0,\
                   1, 0, 0, 0, 1, 0]
   
    >>> find_path(t, (2, 0), (4, 1))
    [(2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 3), \
(3, 4), (4, 4), (5, 4), (5, 3), (5, 2), (5, 1), (4, 1)]
    """
    # tiles to check (tuples of (x, y), cost)
    todo = pqueue.PQueue()
    todo.update(start, 0)
    
    # tiles we've been to
    visited = set()
    
    # associated G and H costs for each tile (tuples of G, H)
    costs = { start: (0, helper.manhattan_dist(start, end)) }
    
    # parents for each tile
    parents = {}
    
    while todo and (end not in visited):
        todo.tie_breaker = lambda a,b: better_tile(a, b, start, end)
    
        cur, c = todo.pop_smallest()
        cur_data = tilemap.tile_data(cur)
        visited.add(cur)
        
        # check neighbours
        for n in tilemap.tile_neighbours(cur):
            # skip it if it doesn't exist, if we've already checked it, or
            # if it isn't passable
            if ((n in visited) or
                (not passable(tilemap.tile_data(n), n))):
                continue
            
            if n not in todo:
                # we haven't looked at this tile yet, so calculate its costs
                g = costs[cur][0] + cost(cur_data)
                h = manhattan_dist(n, end)
                costs[n] = (g, h)
                parents[n] = cur
                todo.update(n, g + h)
            else:
                # if we've found a better path, update it
                g, h = costs[n]
                new_g = costs[cur][0] + cost(cur_data)
                if new_g < g:
                    g = new_g
                    todo.update(n, g + h)
                    costs[n] = (g, h)
                    parents[n] = cur
    
    # we didn't find a path
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
    
def reachable_tiles(tilemap,
                      start,
                      max_cost,
                      cost = lambda tile: 1,
                      passable = lambda tile, pos: tile.passable):
    """
    Returns a set of tiles which can be reached with a total cost of
    max_cost.
    
    Example use:
    >>> t = TileMap("assets/tiles.png", 20, 20, 5, 5)
    >>> t.tiles = [0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0,\
                   0, 0, 0, 0, 0]
    
    >>> reachable_tiles(t, (2, 2), 2) == set([(2, 0), (1, 1), (2, 1), (3, 1), \
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), \
        (2, 4)])
    True
    
    >>> t = TileMap("assets/tiles.png", 20, 20, 6, 6)
    >>> t.tiles = [0, 0, 0, 0, 1, 0,\
                   0, 1, 1, 1, 0, 0,\
                   0, 0, 0, 0, 1, 0,\
                   0, 1, 1, 0, 1, 0,\
                   0, 0, 1, 0, 0, 0,\
                   1, 0, 0, 0, 1, 0]
   
    >>> reachable_tiles(t, (2, 0), 6) == set([(3, 0), (2, 0), (1, 0), \
        (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2)])
    True
    """
    # tiles to check (tuples of x, y)
    todo = pqueue.PQueue()
    todo.update(start, 0)
    
    # tiles we've been to
    visited = set()
    
    # tiles which we can get to within max_cost
    reachable = set()
    reachable.add(start)
    
    while todo:
        cur, c = todo.pop_smallest()
        cur_data = tilemap.tile_data(cur)
        visited.add(cur)
        
        # it's too expensive to get here, so don't bother checking
        if c > max_cost:
            continue
        
        # check neighbours
        for n in tilemap.tile_neighbours(cur):
            # skip it if it doesn't exist, if we've already checked it, or
            # if it isn't passable
            if ((n in visited) or
                (not passable(tilemap.tile_data(n), n))):
                continue
            
            # try updating the tile's cost
            new_cost = c + cost(cur_data)
            if todo.update(n, new_cost) and new_cost <= max_cost:
                reachable.add(n)
    
    return reachable
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
