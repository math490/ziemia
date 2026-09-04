"""Animated player sprite and movement logic."""

from pathlib import Path
from typing import Dict, Optional

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

    def update(self, delta_time: float, ground_y: float, max_x: float):
        """Update movement, gravity, bounds, and animation."""
        self.action_timer = max(0.0, self.action_timer - delta_time)
        self.velocity_y -= self.gravity * delta_time
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time

        floor_y = ground_y + self.height / 2
        if self.center_y <= floor_y:
            self.center_y = floor_y
            self.velocity_y = 0.0
            self.on_ground = True
        else:
            self.on_ground = False

        self.center_x = max(self.width / 2, min(max_x - self.width / 2, self.center_x))
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
