import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from core.constants import GameState, DARK
from managers.game_state_manager import GameStateManager

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    gsm = GameStateManager(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if gsm.state == GameState.MAIN_MENU:
            result = gsm.menu.update(dt, events)
            if result:
                r = gsm.handle_menu_result(result)
                if r == "quit":
                    running = False

        elif gsm.state == GameState.INTRO_CUTSCENE:
            if gsm.intro and gsm.intro.update(dt, events):
                gsm.state = GameState.CHARACTER_SELECT

        elif gsm.state == GameState.CHARACTER_SELECT:
            result = gsm.char_select.update(dt, events)
            if result == "back":
                gsm.state = GameState.MAIN_MENU
            elif result:
                gsm.handle_char_select_result(result)

        elif gsm.state == GameState.ENDING_CUTSCENE:
            if gsm.ending and gsm.ending.update(dt, events):
                gsm.state = GameState.MAIN_MENU
                gsm.audio.play_music("bgm_menu")

        elif gsm.state == GameState.PAUSED:
            result = gsm.pause_menu.update(dt, events)
            if result:
                gsm.handle_pause_result(result)

        elif gsm.state == GameState.GAME_OVER:
            for event in events:
                gsm.handle_game_over_event(event)

        else:
            for event in events:
                r = gsm.handle_events([event])
                if r == "quit":
                    running = False

        gsm.update(dt)
        screen.fill(DARK)
        gsm.render()
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
