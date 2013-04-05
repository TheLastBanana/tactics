import sys, pygame, tiles
from gui import GUI
import unit.base_unit

# Initialize everything
pygame.init()
main_gui = GUI(pygame.Rect(0, 0, 800, 600), (0, 0, 0))
main_gui.load_level("maps/basic.lvl")
clock = pygame.time.Clock()

# The main game loop
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        # End if q is pressed
        elif (event.type == pygame.KEYDOWN and
        (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)):
            pygame.display.quit()
            sys.exit()
        # Respond to clicks
        elif event.type == pygame.MOUSEBUTTONUP:
            main_gui.on_click(event)
    main_gui.update()
    main_gui.draw()
    clock.tick(60)
