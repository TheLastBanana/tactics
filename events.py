import pygame

class EventManager:
    """
    A class which handles pygame events and stores them for the frame.
    """
    def __init__(self):
        self._events = []
    
    def update(self):
        """
        Get all the events and store them for the frame.
        """
        self._events = pygame.event.get()

    def check_event(self, event_type):
        """
        Checks whether the given event occurred this frame, and, if so, returns
        the event.
        Otherwise, returns None.
        """
        # Cycle through the event queue for this frame
        for event in self._events:
            # This is the event we're looking for
            if event.type == event_type:
                return event
        
        return None

    def key_down(self, key):
        """
        Shortcut function to check if a given key was pressed.
        Returns the function if it occurred, or None otherwise.
        """
        # Look for a key down event
        event = self.check_event(pygame.KEYDOWN)
            
        # Check if it is the correct key
        if event and event.key == key:
            return event
            
        return None
