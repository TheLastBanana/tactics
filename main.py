import sys, pygame, tiles
from gui import GUI
from events import EventManager
import unit.base_unit

# Initialize pygame
pygame.init()

# Initialize the GUI
main_gui = GUI(pygame.Rect(0, 0, 800, 600), (0, 0, 0))
main_gui.load_level("maps/basic.lvl")

# Initialize the event manager
event_man = EventManager()

# Initialize the clock
clock = pygame.time.Clock()

# The main game loop
while 1:
    # Get new events
    event_man.update()
    
    # Quit when the window is closed or Q/ESC is pressed.
    if (event_man.check_event(pygame.QUIT)
    or event_man.is_key_down(pygame.K_ESCAPE)
    or event_man.is_key_down(pygame.K_q)):
        pygame.display.quit()
        sys.exit()

    main_gui.draw()
    clock.tick(60)
