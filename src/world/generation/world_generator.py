from __future__ import annotations

from .perlin import PerlinNoise2D

TILE_AIR = 9
TILE_WATER = 0
TILE_SAND = 1
TILE_GRASS = 2
TILE_DIRT = 3
TILE_STONE = 4
TILE_COAL = 5
TILE_IRON = 6
TILE_GOLD = 7
TILE_CAVE = 8

TILE_NAMES = {
    TILE_AIR: "air",
    TILE_WATER: "water",
    TILE_SAND: "sand",
    TILE_GRASS: "grass",
    TILE_DIRT: "dirt",
    TILE_STONE: "stone",
    TILE_COAL: "coal",
    TILE_IRON: "iron",
    TILE_GOLD: "gold",
    TILE_CAVE: "cave",
}

TILE_COLORS = {
    TILE_AIR: (18, 22, 32),
    TILE_WATER: (52, 120, 200),
    TILE_SAND: (225, 191, 111),
    TILE_GRASS: (88, 176, 104),
    TILE_DIRT: (131, 92, 62),
    TILE_STONE: (127, 131, 138),
    TILE_COAL: (52, 52, 56),
    TILE_IRON: (164, 166, 171),
    TILE_GOLD: (217, 185, 62),
    TILE_CAVE: (39, 42, 49),
}


class WorldGenerator:
    """Gera um mapa em camadas com ar acima do terreno e solo abaixo do centro do mundo."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.height_noise = PerlinNoise2D(seed)
        self.cave_noise = PerlinNoise2D(seed + 11)
        self.ore_noise = PerlinNoise2D(seed + 77)

    def _surface_level(self, x: int, width: int, height: int) -> int:
        central_surface = int(height * 0.62)
        nx = x / max(width, 1) * 3.4
        noise = self.height_noise.fractal(nx, 0.25, octaves=5, persistence=0.55)
        offset = int((noise - 0.5) * 18)
        return max(10, min(height - 10, central_surface + offset))

    def _cave_value(self, x: int, y: int, width: int, height: int) -> float:
        nx = x / max(width, 1) * 6.0
        ny = y / max(height, 1) * 6.0
        return self.cave_noise.fractal(nx, ny, octaves=4, persistence=0.6)

    def _ore_value(self, x: int, y: int, width: int, height: int) -> float:
        nx = x / max(width, 1) * 7.0
        ny = y / max(height, 1) * 7.0
        return self.ore_noise.fractal(nx, ny, octaves=3, persistence=0.6)

    def generate(self, width: int, height: int) -> list[list[int]]:
        world: list[list[int]] = []
        center_x = width // 2

        for y in range(height):
            row: list[int] = []
            for x in range(width):
                surface_y = self._surface_level(x, width, height)

                if x == center_x:
                    surface_y = max(10, min(height - 10, int(height * 0.62)))

                if y < surface_y:
                    tile = TILE_AIR
                elif y == surface_y:
                    tile = TILE_GRASS
                elif y <= surface_y + 2:
                    tile = TILE_DIRT
                elif y <= surface_y + 6:
                    tile = TILE_STONE
                else:
                    tile = TILE_STONE

                cave_value = self._cave_value(x, y, width, height)
                ore_value = self._ore_value(x, y, width, height)

                if y > surface_y + 6 and cave_value > 0.72:
                    tile = TILE_CAVE

                if y > surface_y + 8 and tile != TILE_CAVE:
                    if ore_value > 0.82:
                        tile = TILE_COAL
                    elif ore_value > 0.88:
                        tile = TILE_IRON
                    elif ore_value > 0.94:
                        tile = TILE_GOLD

                if y > height - 10:
                    tile = TILE_STONE

                row.append(tile)
            world.append(row)

        return world

    @staticmethod
    def get_color(category: int) -> tuple[int, int, int]:
        return TILE_COLORS.get(category, (255, 0, 255))

    @staticmethod
    def get_name(category: int) -> str:
        return TILE_NAMES.get(category, "unknown")
