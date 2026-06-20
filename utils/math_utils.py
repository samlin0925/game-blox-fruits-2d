import math

def distance(p1, p2) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def normalize(dx, dy):
    length = math.hypot(dx, dy)
    if length == 0:
        return 0.0, 0.0
    return dx / length, dy / length

def angle_to(p1, p2) -> float:
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(val, lo, hi):
    return max(lo, min(hi, val))
