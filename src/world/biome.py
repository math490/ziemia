from dataclasses import dataclass


@dataclass(frozen=True)
class Biome:
    name: str
    surface_color: tuple[int, int, int]
    depth_color: tuple[int, int, int]
    terrain_height: int = 0


FOREST = Biome("floresta", (76, 163, 79), (29, 87, 44), 12)
PLAINS = Biome("planicie", (140, 201, 115), (89, 116, 67), 10)
DESERT = Biome("deserto", (212, 189, 120), (169, 131, 82), 8)
TAIGA = Biome("taiga", (99, 130, 104), (46, 72, 60), 11)
CAVERN = Biome("caverna", (42, 46, 54), (17, 17, 22), 4)

BIOMES = {
    "floresta": FOREST,
    "planicie": PLAINS,
    "deserto": DESERT,
    "taiga": TAIGA,
    "caverna": CAVERN,
}
