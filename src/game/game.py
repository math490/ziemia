"""Main game class for Ziemia."""

import arcade

from entities.player import Player
from world.blocks import BlockWorld

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Ziemia - A Terraria-style Adventure"
PLAYER_ASSET_DIR = "assets/images/player"
WORLD_WIDTH = 6400
BLOCK_SIZE = 32
WORLD_EDGE_BLOCKS = 10
PLAYABLE_MIN_X = BLOCK_SIZE * WORLD_EDGE_BLOCKS
PLAYABLE_MAX_X = WORLD_WIDTH - PLAYABLE_MIN_X
CAMERA_FOLLOW_SPEED = 8.0
CAMERA_MARGIN = 96
BLOCK_INTERACTION_RANGE = BLOCK_SIZE * 6
HOTBAR_SLOTS = 10
HOTBAR_SLOT_SIZE = 48
HOTBAR_GAP = 6
HOTBAR_LEFT_MARGIN = 20
HOTBAR_TOP_MARGIN = 20


class ZiemiaGame(arcade.Window):
    """Main game window for Ziemia."""

    def __init__(self):
        """Initialize the game."""
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            resizable=True,
            vsync=True,
        )
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.world_camera.match_window()
        self._sync_gui_camera()
        self.camera_zoom = 1.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0

        self.frame_count = 0
        self.left_pressed = False
        self.right_pressed = False
        self.jump_requested = False
        self.selected_slot = 0
        self.ground_y = 80
        self.player = Player(WORLD_WIDTH / 2, 220, PLAYER_ASSET_DIR)
        self.block_world = BlockWorld(WORLD_WIDTH, BLOCK_SIZE, self.ground_y)
        self.terrain_shapes = self.block_world.sprites
        self.selected_slot = 0
        self.camera_target_x = self.player.center_x
        self.camera_target_y = self.player.center_y

    def setup(self):
        """Set up the game."""
        self.player = Player(WORLD_WIDTH / 2, 220, PLAYER_ASSET_DIR)
        self.block_world = BlockWorld(WORLD_WIDTH, BLOCK_SIZE, self.ground_y)
        self.terrain_shapes = self.block_world.sprites
        self.selected_slot = 0
        self.camera_target_x = self.player.center_x
        self.camera_target_y = self.player.center_y
        self._update_camera(0.0)

    def _update_camera(self, delta_time: float):
        """Smoothly follow the player while keeping the camera in world bounds."""
        self.camera_target_x = self.player.center_x
        self.camera_target_y = max(self.height / (2 * self.camera_zoom), self.player.center_y)

        view_width = self.width / self.camera_zoom
        view_height = self.height / self.camera_zoom
        min_x = PLAYABLE_MIN_X + view_width / 2
        max_x = max(min_x, PLAYABLE_MAX_X - view_width / 2)
        min_y = view_height / 2
        max_y = max(min_y, 1600 - view_height / 2)

        target_x = max(min_x, min(max_x, self.camera_target_x))
        target_y = max(min_y, min(max_y, self.camera_target_y))
        current_x, current_y = self.world_camera.position
        smoothing = 1.0 if delta_time <= 0 else 1.0 - pow(2.71828, -CAMERA_FOLLOW_SPEED * delta_time)
        self.world_camera.position = (
            current_x + (target_x - current_x) * smoothing,
            current_y + (target_y - current_y) * smoothing,
        )
        self.world_camera.zoom = self.camera_zoom
        self._update_terrain_culling(view_width, view_height)

    def _sync_gui_camera(self):
        """Keep screen-space HUD coordinates aligned with the current window."""
        self.gui_camera.match_window()
        self.gui_camera.position = (self.width / 2, self.height / 2)
        self.gui_camera.zoom = 1.0

    def _update_terrain_culling(self, view_width: float, view_height: float):
        """Hide terrain sprites outside the camera view plus a small preload margin."""
        camera_x, camera_y = self.world_camera.position
        left = camera_x - view_width / 2 - CAMERA_MARGIN
        right = camera_x + view_width / 2 + CAMERA_MARGIN
        bottom = camera_y - view_height / 2 - CAMERA_MARGIN
        top = camera_y + view_height / 2 + CAMERA_MARGIN

        self.block_world.cull(left, right, bottom, top, CAMERA_MARGIN)

    def run(self):
        """Run the game."""
        self.setup()
        arcade.run()

    def on_draw(self):
        """Render the game screen."""
        self.clear()

        self.world_camera.use()

        self.terrain_shapes.draw()

        # draw the ground line
        arcade.draw_lrbt_rectangle_filled(
            0,
            WORLD_WIDTH,
            0,
            self.ground_y,
            arcade.color.GREEN
        )

        self.player.draw()

        self.gui_camera.use()

        self._draw_hud()

    def _draw_hud(self):
        """Draw the player's ten-slot hotbar in screen space."""
        total_width = (
            HOTBAR_SLOTS * HOTBAR_SLOT_SIZE
            + (HOTBAR_SLOTS - 1) * HOTBAR_GAP
        )
        start_x = HOTBAR_LEFT_MARGIN
        top = self.height - HOTBAR_TOP_MARGIN
        bottom = top - HOTBAR_SLOT_SIZE
        inventory = self.player.inventory

        for slot_index in range(HOTBAR_SLOTS):
            left = start_x + slot_index * (HOTBAR_SLOT_SIZE + HOTBAR_GAP)
            right = left + HOTBAR_SLOT_SIZE
            is_selected = slot_index == self.selected_slot
            border_color = arcade.color.GOLD if is_selected else arcade.color.DARK_GRAY
            fill_color = arcade.color.DARK_SLATE_GRAY if is_selected else arcade.color.BLACK

            arcade.draw_lrbt_rectangle_filled(
                left,
                right,
                bottom,
                bottom + HOTBAR_SLOT_SIZE,
                border_color,
            )
            arcade.draw_lrbt_rectangle_filled(
                left + 3,
                right - 3,
                bottom + 3,
                bottom + HOTBAR_SLOT_SIZE - 3,
                fill_color,
            )

            item = inventory[slot_index]
            if item:
                arcade.draw_lrbt_rectangle_filled(
                    left + 12,
                    right - 12,
                    bottom + 12,
                    bottom + HOTBAR_SLOT_SIZE - 12,
                    item["color"],
                )
                arcade.draw_text(
                    str(item["quantity"]),
                    right - 7,
                    bottom + 5,
                    arcade.color.WHITE,
                    font_size=10,
                    anchor_x="right",
                )

            arcade.draw_text(
                "0" if slot_index == 9 else str(slot_index + 1),
                left + 5,
                bottom + HOTBAR_SLOT_SIZE - 14,
                arcade.color.WHITE,
                font_size=10,
            )

    def on_update(self, delta_time):
        """Update game logic."""
        self.frame_count += 1
        delta_time = min(delta_time, 1 / 30)

        move_direction = 0.0
        if self.left_pressed:
            move_direction -= 1.0
        if self.right_pressed:
            move_direction += 1.0
        self.player.move(move_direction)

        if self.jump_requested:
            self.player.jump()
            self.jump_requested = False

        self.player.update(
            delta_time,
            self.ground_y,
            PLAYABLE_MAX_X,
            PLAYABLE_MIN_X,
            self.block_world.collision_rects(self.player.center_x),
        )
        self._update_camera(delta_time)

    def on_key_press(self, key, modifiers):
        """Handle key presses."""
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.F4:
            self.set_fullscreen(not self.fullscreen)
            self.world_camera.match_window()
            self._sync_gui_camera()
            self._update_camera(0.0)
        elif key in (arcade.key.PLUS, arcade.key.NUM_ADD):
            self.camera_zoom = min(2.0, self.camera_zoom + 0.1)
            self._update_camera(0.0)
        elif key in (arcade.key.MINUS, arcade.key.NUM_SUBTRACT):
            self.camera_zoom = max(0.6, self.camera_zoom - 0.1)
            self._update_camera(0.0)
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.jump_requested = True
        elif key in (arcade.key.KEY_1, arcade.key.NUM_1):
            self.selected_slot = 0
        elif key in (arcade.key.KEY_2, arcade.key.NUM_2):
            self.selected_slot = 1
        elif key in (arcade.key.KEY_3, arcade.key.NUM_3):
            self.selected_slot = 2
        elif key in (arcade.key.KEY_4, arcade.key.NUM_4):
            self.selected_slot = 3
        elif key in (arcade.key.KEY_5, arcade.key.NUM_5):
            self.selected_slot = 4
        elif key in (arcade.key.KEY_6, arcade.key.NUM_6):
            self.selected_slot = 5
        elif key in (arcade.key.KEY_7, arcade.key.NUM_7):
            self.selected_slot = 6
        elif key in (arcade.key.KEY_8, arcade.key.NUM_8):
            self.selected_slot = 7
        elif key in (arcade.key.KEY_9, arcade.key.NUM_9):
            self.selected_slot = 8
        elif key in (arcade.key.KEY_0, arcade.key.NUM_0):
            self.selected_slot = 9

    def on_key_release(self, key, modifiers):
        """Handle key releases."""
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse button presses."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._try_break_block(x, y)
            self.player.attack()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self._try_place_selected_block(x, y)

    def _try_break_block(self, screen_x: float, screen_y: float):
        """Break a nearby block under the cursor and collect its item."""
        world_position = self.world_camera.unproject((screen_x, screen_y))
        cell = self.block_world.world_to_cell(world_position.x, world_position.y)
        block_center = self.block_world.cell_to_world_center(cell)
        distance_x = block_center[0] - self.player.center_x
        distance_y = block_center[1] - self.player.center_y
        if distance_x * distance_x + distance_y * distance_y > BLOCK_INTERACTION_RANGE ** 2:
            return

        block_name = self.block_world.blocks.get(cell)
        if block_name is None or not self.player.can_collect_block(block_name):
            return

        removed_block = self.block_world.remove_block(cell)
        if removed_block is not None:
            self.player.collect_block(removed_block)
            self._update_camera(0.0)

    def _try_place_selected_block(self, screen_x: float, screen_y: float):
        """Place the selected hotbar block at the cell under the cursor."""
        item = self.player.inventory[self.selected_slot]
        if not item or item["quantity"] <= 0:
            return

        world_position = self.world_camera.unproject((screen_x, screen_y))
        cell = self.block_world.world_to_cell(world_position.x, world_position.y)
        cell_x = cell[0] * BLOCK_SIZE + BLOCK_SIZE / 2
        cell_y = self.ground_y + cell[1] * BLOCK_SIZE + BLOCK_SIZE / 2

        playable_min_cell = PLAYABLE_MIN_X // BLOCK_SIZE
        playable_max_cell = PLAYABLE_MAX_X // BLOCK_SIZE
        if not playable_min_cell <= cell[0] <= playable_max_cell:
            return

        player_overlap = (
            abs(cell_x - self.player.center_x) < (BLOCK_SIZE + self.player.width) / 2
            and abs(cell_y - self.player.center_y) < (BLOCK_SIZE + self.player.height) / 2
        )
        if player_overlap:
            return

        if self.block_world.place_block(cell, item["block"]):
            item["quantity"] -= 1
            self._update_camera(0.0)

    def on_resize(self, width, height):
        """Keep both cameras aligned after manual resizing or fullscreen changes."""
        super().on_resize(width, height)
        self.world_camera.match_window()
        self._sync_gui_camera()
        self._update_camera(0.0)
