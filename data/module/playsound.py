#
import pygame
import os
def play_sound(sound_file, volume=0.5):
   
    if not os.path.exists(sound_file):
        print(f"Sound file '{sound_file}' does not exist.")
        return
    
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Load and play the sound
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
    print(f"▶️ Playing sound: {sound_file}")
    
    # Wait until the sound finishes playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Check every 100ms