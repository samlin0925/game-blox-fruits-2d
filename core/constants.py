from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    INTRO_CUTSCENE = auto()
    CHARACTER_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    ENDING_CUTSCENE = auto()
    CHEAT_INPUT = auto()
    GACHA_UI = auto()
    CHEAT_MENU = auto()

class AIState(Enum):
    IDLE = auto()
    PATROL = auto()
    CHASE = auto()
    ATTACK = auto()
    DEAD = auto()
    STUNNED = auto()

class DamageType(Enum):
    NORMAL = auto()
    CRITICAL = auto()
    SKILL = auto()
    FIRE = auto()
    ICE = auto()

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
RED    = (220, 50,  50 )
GREEN  = (50,  200, 80 )
BLUE   = (50,  100, 220)
YELLOW = (255, 215, 0  )
ORANGE = (255, 140, 0  )
PURPLE = (150, 50,  200)
CYAN   = (0,   200, 220)
GRAY   = (100, 100, 100)
DARK   = (20,  20,  30 )
GOLD   = (255, 215, 0  )
TRANSPARENT_BLACK = (0, 0, 0, 160)

FONT_LARGE  = 48
FONT_MEDIUM = 32
FONT_SMALL  = 22
FONT_TINY   = 16
