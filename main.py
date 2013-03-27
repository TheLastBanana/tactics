import sys, pygame, tiles
from gui import GUI

pygame.init()
main_gui = GUI(pygame.Rect(0, 0, 640, 480), (0, 0, 0))
clock = pygame.time.Clock()
    
test_map = tiles.TileMap(main_gui.screen, "assets/tiles.png", 24, 24, 20, 20)
main_gui.add(test_map)

while 1:
    for event in pygame.event.get():
	    if event.type == pygame.QUIT:
		    pygame.display.quit()
		    sys.exit()

    main_gui.draw()
    clock.tick(60)
