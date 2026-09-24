import math
import random


class PerlinNoise2D:
    """Implementação pura de Perlin noise em 2D para uso no gerador de mapa."""

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.permutation = list(range(256))
        self.rng.shuffle(self.permutation)
        self.permutation *= 2

    @staticmethod
    def fade(t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    @staticmethod
    def grad(hash_value: int, x: float, y: float) -> float:
        h = hash_value & 7
        u = x if h < 4 else y
        v = y if h < 4 else x
        return ((h & 1) * 2 - 1) * u + (((h >> 1) & 1) * 2 - 1) * v

    def noise(self, x: float, y: float) -> float:
        x0 = math.floor(x)
        y0 = math.floor(y)
        xf = x - x0
        yf = y - y0

        u = self.fade(xf)
        v = self.fade(yf)

        aa = self.permutation[(x0 + self.permutation[y0 & 255]) & 255]
        ba = self.permutation[(x0 + 1 + self.permutation[y0 & 255]) & 255]
        ab = self.permutation[(x0 + self.permutation[(y0 + 1) & 255]) & 255]
        bb = self.permutation[(x0 + 1 + self.permutation[(y0 + 1) & 255]) & 255]

        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        return self.lerp(x1, x2, v)

    def fractal(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0

        if max_value == 0:
            return 0.0
        return total / max_value
