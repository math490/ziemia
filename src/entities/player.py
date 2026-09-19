"""Animated player sprite and movement logic."""

from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import arcade
from PIL import Image


class Player(arcade.Sprite):
    """Player sprite with state-based animation and simple physics."""

    ANIMATION_STATES = ("idle", "run", "jump", "fall", "action")

    def __init__(self, x: float, y: float, asset_dir: Optional[str] = None):
        """Create a player using external PNGs when available, or placeholders."""
        super().__init__()
        self.width = 32
        self.height = 64
        self.center_x = x
        self.center_y = y

        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.inventory = [
            {"name": "Terra", "block": "dirt", "color": arcade.color.BROWN, "quantity": 12},
            {"name": "Pedra", "block": "stone", "color": arcade.color.GRAY, "quantity": 8},
            {"name": "Grama", "block": "grass", "color": arcade.color.DARK_GREEN, "quantity": 5},
            {"name": "Tocha", "block": "dirt", "color": arcade.color.ORANGE, "quantity": 3},
            None,
            None,
            None,
            None,
            None,
            None,
        ]

        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = 260.0
        self.jump_strength = 520.0
        self.gravity = 1200.0
        self.on_ground = False
        self.facing_right = True

        self.state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.12
        self.action_timer = 0.0
        self.state_textures = self._load_textures(asset_dir)
        self.flipped_textures: Dict[str, arcade.Texture] = {}
        self.texture = self.state_textures["idle"][0]
        self.scale_x = 0.5
        self.scale_y = 1.0

    def _load_textures(self, asset_dir: Optional[str]) -> Dict[str, list]:
        """Load state PNGs or create lightweight procedural placeholders.

        Expected optional files: ``idle.png``, ``run_0.png``, ``run_1.png``,
        ``jump.png``, ``fall.png`` and ``action.png``.
        """
        textures: Dict[str, list] = {}
        asset_path = Path(asset_dir) if asset_dir else None

        for state in self.ANIMATION_STATES:
            files = sorted(asset_path.glob(f"{state}*.png")) if asset_path else []
            if files:
                textures[state] = [arcade.load_texture(str(path)) for path in files]
            else:
                colors = {
                    "idle": arcade.color.WHITE,
                    "run": arcade.color.YELLOW,
                    "jump": arcade.color.CYAN,
                    "fall": arcade.color.LIGHT_BLUE,
                    "action": arcade.color.ORANGE,
                }
                frame_count = 2 if state in ("idle", "run") else 1
                textures[state] = [
                    arcade.make_soft_square_texture(64, colors[state], 255, 220)
                    for _ in range(frame_count)
                ]
        return textures

    def move(self, direction: float):
        """Set horizontal movement direction and remember facing."""
        self.velocity_x = direction * self.speed
        if direction < 0:
            self.facing_right = False
        elif direction > 0:
            self.facing_right = True
        self.scale_x = 0.5 if self.facing_right else -0.5

    def jump(self):
        """Jump if the player is on the ground."""
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False

    def attack(self):
        """Trigger a short action animation."""
        self.action_timer = 0.22

    def _select_state(self):
        """Select the visual state from movement and physics."""
        if self.action_timer > 0:
            return "action"
        if not self.on_ground:
            return "jump" if self.velocity_y > 0 else "fall"
        return "run" if abs(self.velocity_x) > 1 else "idle"

    def _animate(self, delta_time: float):
        """Advance only the current state's frames."""
        next_state = self._select_state()
        if next_state != self.state:
            self.state = next_state
            self.animation_frame = 0
            self.animation_timer = 0.0

        frames = self.state_textures[self.state]
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.animation_frame = (self.animation_frame + 1) % len(frames)
        self.texture = frames[self.animation_frame]

    def update(
        self,
        delta_time: float,
        ground_y: float,
        max_x: float,
        min_x: float = 0.0,
        solid_blocks: Optional[Iterable[Tuple[float, float, float, float]]] = None,
    ):
        """Update movement, gravity, bounds, and animation."""
        previous_x = self.center_x
        previous_y = self.center_y
        self.action_timer = max(0.0, self.action_timer - delta_time)
        rectangles = tuple(solid_blocks or ())
        half_width = self.width / 2
        half_height = self.height / 2

        # Resolve horizontal movement independently so a wall cannot be crossed
        # because vertical movement changed the overlap state in the same frame.
        self.center_x += self.velocity_x * delta_time
        for left, right, bottom, top in rectangles:
            overlaps_y = self.center_y + half_height > bottom and self.center_y - half_height < top
            overlaps_x = self.center_x + half_width > left and self.center_x - half_width < right
            crossed_from_left = previous_x + half_width <= left and self.center_x + half_width >= left
            crossed_from_right = previous_x - half_width >= right and self.center_x - half_width <= right
            if not overlaps_y or (not overlaps_x and not crossed_from_left and not crossed_from_right):
                continue
            if self.velocity_x >= 0 and (overlaps_x or crossed_from_left):
                self.center_x = left - half_width
            else:
                self.center_x = right + half_width
            self.velocity_x = 0.0

        # Apply world limits after horizontal block resolution.
        self.center_x = max(
            min_x + half_width,
            min(max_x - half_width, self.center_x),
        )

        # Resolve vertical movement independently for stable floors and ceilings.
        self.velocity_y -= self.gravity * delta_time
        self.center_y += self.velocity_y * delta_time

        self.on_ground = False
        for left, right, bottom, top in rectangles:
            overlaps_x = self.center_x + half_width > left and self.center_x - half_width < right
            overlaps_y = self.center_y + half_height > bottom and self.center_y - half_height < top
            crossed_from_below = previous_y + half_height <= bottom and self.center_y + half_height >= bottom
            crossed_from_above = previous_y - half_height >= top and self.center_y - half_height <= top
            if not overlaps_x or (not overlaps_y and not crossed_from_below and not crossed_from_above):
                continue

            if self.velocity_y <= 0 and (overlaps_y or crossed_from_above):
                self.center_y = top + half_height
                self.velocity_y = 0.0
                self.on_ground = True
            else:
                self.center_y = bottom - half_height
                self.velocity_y = 0.0

        floor_y = ground_y + self.height / 2
        if self.center_y <= floor_y and self.velocity_y <= 0:
            self.center_y = floor_y
            self.velocity_y = 0.0
            self.on_ground = True

        self._animate(delta_time)

    def draw(self):
        """Render the current texture without Arcade's incompatible SpriteList path."""
        texture = self.texture
        if not self.facing_right:
            cache_key = f"{self.state}:{self.animation_frame}"
            texture = self.flipped_textures.get(cache_key)
            if texture is None:
                image = self.texture.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                texture = arcade.Texture(image)
                self.flipped_textures[cache_key] = texture

        draw_width = self.width * abs(self.scale_x)
        draw_height = self.height * self.scale_y
        arcade.draw_texture_rect(
            texture,
            arcade.LBWH(
                self.center_x - draw_width / 2,
                self.center_y - draw_height / 2,
                draw_width,
                draw_height,
            ),
            pixelated=True,
        )

    def take_damage(self, amount: int):
        """Take damage."""
        self.health = max(0, self.health - amount)

    def heal(self, amount: int):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)

    def collect_block(self, block_name: str) -> bool:
        """Add a mined block to a matching or empty hotbar slot."""
        for item in self.inventory:
            if item and item.get("block") == block_name:
                item["quantity"] += 1
                return True

        colors = {
            "dirt": arcade.color.BROWN,
            "stone": arcade.color.GRAY,
            "grass": arcade.color.DARK_GREEN,
        }
        for index, item in enumerate(self.inventory):
            if item is None:
                self.inventory[index] = {
                    "name": block_name.title(),
                    "block": block_name,
                    "color": colors.get(block_name, arcade.color.WHITE),
                    "quantity": 1,
                }
                return True
        return False

    def can_collect_block(self, block_name: str) -> bool:
        """Return whether a block can fit in the hotbar."""
        return any(
            item is None or item.get("block") == block_name
            for item in self.inventory
        )
