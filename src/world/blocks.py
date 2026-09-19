"""Grid-based block world used by the playable prototype."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import arcade
from PIL import Image


@dataclass(frozen=True)
class BlockType:
    """Visual and gameplay data for one block type."""

    name: str
    color: Tuple[int, int, int]
    placed_color: Tuple[int, int, int]
    solid: bool


BLOCK_TYPES: Dict[str, BlockType] = {
    "grass": BlockType("grass", arcade.color.DARK_GREEN, arcade.color.GREEN, False),
    "dirt": BlockType("dirt", arcade.color.BROWN, arcade.color.LIGHT_BROWN, True),
    "stone": BlockType("stone", arcade.color.GRAY, arcade.color.LIGHT_GRAY, True),
}


class BlockWorld:
    """Own the block grid and its batched Arcade sprites."""

    def __init__(self, width: int, block_size: int, ground_y: int):
        self.width = width
        self.block_size = block_size
        self.ground_y = ground_y
        self.blocks: Dict[Tuple[int, int], str] = {}
        self.sprites = arcade.SpriteList()
        self._sprites_by_cell: Dict[Tuple[int, int], arcade.Sprite] = {}
        self.placed_cells = set()
        self.generate_base_terrain()

    def generate_base_terrain(self):
        """Generate the prototype terrain into the editable grid."""
        for grid_x in range(self.width // self.block_size + 1):
            height = 1
            if grid_x % 8 == 0:
                height = 2
            if grid_x % 12 == 0:
                height = 3
            for grid_y in range(height):
                block_name = "grass" if grid_y == height - 1 else "dirt"
                self._add_block(grid_x, grid_y, block_name)

    def _add_block(
        self,
        grid_x: int,
        grid_y: int,
        block_name: str,
        placed: bool = False,
    ) -> bool:
        """Add one block and its sprite to the world."""
        cell = (grid_x, grid_y)
        if cell in self.blocks or block_name not in BLOCK_TYPES:
            return False

        block_type = BLOCK_TYPES[block_name]
        color = block_type.placed_color if placed else block_type.color
        image = Image.new(
            "RGBA",
            (self.block_size, self.block_size),
            (color[0], color[1], color[2], 255),
        )
        sprite = arcade.Sprite(arcade.Texture(image))
        sprite.width = self.block_size
        sprite.height = self.block_size
        sprite.center_x = grid_x * self.block_size + self.block_size / 2
        sprite.center_y = self.ground_y + grid_y * self.block_size + self.block_size / 2
        self.blocks[cell] = block_name
        self._sprites_by_cell[cell] = sprite
        if placed:
            self.placed_cells.add(cell)
        self.sprites.append(sprite)
        return True

    def world_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to a grid cell."""
        return (
            int(x // self.block_size),
            int((y - self.ground_y) // self.block_size),
        )

    def cell_to_world_center(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        """Return the world-space center of a grid cell."""
        grid_x, grid_y = cell
        return (
            grid_x * self.block_size + self.block_size / 2,
            self.ground_y + grid_y * self.block_size + self.block_size / 2,
        )

    def place_block(self, cell: Tuple[int, int], block_name: str) -> bool:
        """Place a block if the cell is empty and within the world."""
        grid_x, grid_y = cell
        if grid_x < 0 or grid_x > self.width // self.block_size:
            return False
        if grid_y < 0 or cell in self.blocks:
            return False
        return self._add_block(grid_x, grid_y, block_name, placed=True)

    def get_sprite(self, cell: Tuple[int, int]) -> Optional[arcade.Sprite]:
        """Return the sprite stored at a cell, if present."""
        return self._sprites_by_cell.get(cell)

    def collision_rects(self, center_x: float, radius: float = 160.0):
        """Return solid block rectangles near a world-space position."""
        left = center_x - radius
        right = center_x + radius
        half = self.block_size / 2
        rectangles = []
        for cell, sprite in self._sprites_by_cell.items():
            block_name = self.blocks[cell]
            if cell not in self.placed_cells or not BLOCK_TYPES[block_name].solid:
                continue
            if left - half <= sprite.center_x <= right + half:
                rectangles.append((
                    sprite.center_x - half,
                    sprite.center_x + half,
                    sprite.center_y - half,
                    sprite.center_y + half,
                ))
        return rectangles

    def remove_block(self, cell: Tuple[int, int]) -> Optional[str]:
        """Remove a block and return its type, or None if the cell is empty."""
        block_name = self.blocks.pop(cell, None)
        sprite = self._sprites_by_cell.pop(cell, None)
        if block_name is None or sprite is None:
            return None

        self.sprites.remove(sprite)
        self.placed_cells.discard(cell)
        return block_name

    def cull(self, left: float, right: float, bottom: float, top: float, margin: float):
        """Update sprite visibility using a camera rectangle."""
        for sprite in self.sprites:
            sprite.visible = (
                left - margin <= sprite.center_x <= right + margin
                and bottom - margin <= sprite.center_y <= top + margin
            )
