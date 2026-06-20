import pygame

_cached_name = ""
_cache = {}

def _find_font() -> str:
    global _cached_name
    if _cached_name:
        return _cached_name
    candidates = [
        "microsoftyaheiui",
        "microsoftyahei",
        "microsoftjhengheiui",
        "microsoftjhenghei",
        "simsun",
        "nsimsun",
    ]
    available = set(pygame.font.get_fonts())
    for name in candidates:
        if name in available:
            _cached_name = name
            return name
    _cached_name = ""
    return ""

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key in _cache:
        return _cache[key]
    name = _find_font()
    try:
        font = pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        font = pygame.font.SysFont(None, size, bold=bold)
    _cache[key] = font
    return font
