"""Main game class for Ziemia."""

import arcade

from entities.player import Player
from world.terrain import TerrainGenerator

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Ziemia - A Terraria-style Adventure"


class ZiemiaGame(arcade.Window):
    """Main game window for Ziemia."""

    def __init__(self):
        """Initialize the game."""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.frame_count = 0
        self.left_pressed = False
        self.right_pressed = False
        self.jump_requested = False
        self.ground_y = 80
        self.player = Player(150, 220)
        self.terrain = self._generate_terrain()

    def setup(self):
        """Set up the game."""
        self.player = Player(150, 220)
        self.terrain = self._generate_terrain()

    def _generate_terrain(self):
        """Create a simple grid of terrain blocks."""
        terrain = []
        block_size = 32
        for x in range(0, SCREEN_WIDTH + block_size, block_size):
            height = 1
            if (x // block_size) % 8 == 0:
                height = 2
            if (x // block_size) % 12 == 0:
                height = 3
            for y in range(height):
                terrain.append({
                    "x": x + block_size / 2,
                    "y": self.ground_y + (y * block_size) + (block_size / 2),
                    "width": block_size,
                    "height": block_size,
                })
        return terrain

    def run(self):
        """Run the game."""
        self.setup()
        arcade.run()

    def on_draw(self):
        """Render the game screen."""
        arcade.start_render()

        for block in self.terrain:
            arcade.draw_rectangle_filled(
                block["x"],
                block["y"],
                block["width"],
                block["height"],
                arcade.color.DARK_GREEN
            )

        # draw the ground line
        arcade.draw_lrtb_rectangle_filled(
            0,
            SCREEN_WIDTH,
            self.ground_y,
            0,
            arcade.color.GREEN
        )

        arcade.draw_rectangle_filled(
            self.player.x,
            self.player.y,
            self.player.width,
            self.player.height,
            arcade.color.WHITE
        )

        # Simple HUD bar to show a status area without using text rendering.
        arcade.draw_lrtb_rectangle_filled(
            20,
            220,
            SCREEN_HEIGHT - 10,
            SCREEN_HEIGHT - 35,
            arcade.color.DARK_GRAY
        )

    def on_update(self, delta_time):
        """Update game logic."""
        self.frame_count += 1

        move_direction = 0.0
        if self.left_pressed:
            move_direction -= 1.0
        if self.right_pressed:
            move_direction += 1.0
        self.player.move(move_direction)

        if self.jump_requested:
            self.player.jump()
            self.jump_requested = False

        self.player.update(delta_time, self.ground_y, SCREEN_WIDTH)

    def on_key_press(self, key, modifiers):
        """Handle key presses."""
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.jump_requested = True

    def on_key_release(self, key, modifiers):
        """Handle key releases."""
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse button presses."""
        pass
