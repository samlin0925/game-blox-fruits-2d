import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Blox Fruits 2D - 惡魔果實冒險"

WORLD_WIDTH = 3840
WORLD_HEIGHT = 2160

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save_data.json")

ZONE_COLORS = [
    (20, 60, 30),
    (80, 60, 20),
    (40, 15, 10),
]
ZONE_ACCENT = [
    (30, 100, 50),
    (120, 90, 30),
    (70, 25, 15),
]

ZONE_BOUNDARIES = [0, WORLD_WIDTH // 3, WORLD_WIDTH * 2 // 3, WORLD_WIDTH]
ZONE_NAMES = ["新手海島", "火山基地", "傳說城堡"]

ALTAR_POS = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
ALTAR_RADIUS = 60

BOSS_KILL_THRESHOLD = [20, 40, 60]

PLAYER_BASE_SPEED = 200
PROJECTILE_BASE_SPEED = 380
PROJECTILE_LIFETIME = 1.5

ENEMY_SPAWN_INTERVAL = 3.0
MAX_ENEMIES = 20
SPAWN_MARGIN = 200
