import pygame
from pygame.mixer import Sound

class SoundManager:
    """
    A class to manage sounds. Does not initially load any sound file,
    but instead loads on request the first time
    """
    _sounds = {}
    
    def __init__(self):
        """
        """
        pass
    
    @staticmethod
    def play(sound_name):
        """
        Plays a requested sound. If the sound isn't already loaded then
        the sound is loaded first.
        """
        
        # Load sound if not already loaded
        if soundName not in SoundManager:
            SoundManager._load(sound_name)
        
        # Play the sound, no extra args needed, defaults are fine
        _sounds[sound_name].play()
    
    @staticmethod
    def _load(name):
        """
        Loads a .wav file as a pygame.mixer.Sound and places it into the 
        dictionary.
        """
        try:
            # Construct the path
            file_name = "assets/{}.wav".format(name)
            
            # Load from path and save to the dictionary
            _sounds[name] = Sound(file = file_name)
            
            # Return success
            return True
        
        # Problem loading the sound
        except pygame.error:
            print("Exception loading sound file \"{}\".".format(name))
