# functions.py
import pygame
from main import WINDOW_WIDTH,WINDOW_HEIGHT

def toggle_fullscreen(fullscreen, display_surface):
    """Schimbă între mod fullscreen și mod fereastră."""
    if fullscreen:
        # Schimbă la mod fereastră
        display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    else:
        # Schimbă la mod fullscreen
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        display_surface = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    fullscreen = not fullscreen
    
    return fullscreen, display_surface


def toggle_pause(paused):
    """Comută între pauză și reluare."""
    return not paused


def draw_pause_screen(display_surface, window_width, window_height):
    """Afișează ecranul de pauză."""
    font = pygame.font.SysFont('Arial', 50)
    text = font.render('PAUSED', True, (255, 0, 0))
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    display_surface.blit(text, text_rect)
