import sys, pygame, tiles
from gui import GUI

pygame.init()
main_gui = GUI(pygame.Rect(0, 0, 800, 600), (0, 0, 0))
clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        #end if q is pressed
        elif event.type == pygame.KEYDOWN and event.unicode == 'q':
            pygame.display.quit()
            sys.exit()
    main_gui.draw()
    clock.tick(60)
