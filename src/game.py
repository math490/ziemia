import math

import pygame

from src.config import FPS, TILE_SIZE, TITLE, WINDOW_HEIGHT, WINDOW_WIDTH
from src.entities import Player
from src.world.generation import WorldGenerator


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.tile_size = TILE_SIZE
        self.world_generator = WorldGenerator(seed=42)
        self.world = self.world_generator.generate(240, 80)
        self.camera = pygame.Vector2(0, 0)

        self.player = Player(200, 100)
        self._spawn_player_on_surface()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

    def _tile_at_pixel(self, pixel_x: float, pixel_y: float) -> int:
        x = int(pixel_x // self.tile_size)
        y = int(pixel_y // self.tile_size)
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x >= len(self.world[0]):
            x = len(self.world[0]) - 1
        if y >= len(self.world):
            y = len(self.world) - 1
        return self.world[y][x]

    def _spawn_player_on_surface(self) -> None:
        center_x = len(self.world[0]) // 2
        surface_y = 0
        for y in range(len(self.world)):
            if self.world[y][center_x] != 9:
                surface_y = y
                break

        self.player.rect.x = center_x * self.tile_size
        self.player.rect.y = max(0, (surface_y - 33) * self.tile_size)
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.is_on_ground = False

    def _is_solid_tile(self, tile_id: int) -> bool:
        return tile_id not in (9, 0)

    def _resolve_player_collisions(self) -> None:
        player = self.player
        previous_rect = player.prev_rect

        left = int(player.rect.left // self.tile_size)
        right = int((player.rect.right - 1) // self.tile_size)
        top = int(player.rect.top // self.tile_size)
        bottom = int((player.rect.bottom - 1) // self.tile_size)

        left = max(0, min(left, len(self.world[0]) - 1))
        right = max(0, min(right, len(self.world[0]) - 1))
        top = max(0, min(top, len(self.world) - 1))
        bottom = max(0, min(bottom, len(self.world) - 1))

        if player.velocity.x > 0:
            tile_x = right + 1
            if tile_x < len(self.world[0]):
                for y in range(top, bottom + 1):
                    tile = self.world[y][tile_x]
                    if self._is_solid_tile(tile):
                        player.rect.right = tile_x * self.tile_size
                        player.velocity.x = 0
                        break
        elif player.velocity.x < 0:
            tile_x = left
            if tile_x >= 0:
                for y in range(top, bottom + 1):
                    tile = self.world[y][tile_x]
                    if self._is_solid_tile(tile):
                        player.rect.left = (tile_x + 1) * self.tile_size
                        player.velocity.x = 0
                        break

        player.is_on_ground = False
        if player.velocity.y >= 0:
            tile_y = bottom + 1
            if tile_y < len(self.world):
                for x in range(left, right + 1):
                    tile = self.world[tile_y][x]
                    if self._is_solid_tile(tile):
                        if previous_rect.bottom <= (tile_y * self.tile_size):
                            player.rect.bottom = tile_y * self.tile_size
                            player.velocity.y = 0
                            player.is_on_ground = True
                            break
        elif player.velocity.y < 0:
            tile_y = top
            if tile_y >= 0:
                for x in range(left, right + 1):
                    tile = self.world[tile_y][x]
                    if self._is_solid_tile(tile):
                        if previous_rect.top >= ((tile_y + 1) * self.tile_size):
                            player.rect.top = (tile_y + 1) * self.tile_size
                            player.velocity.y = 0
                            break

        if not player.is_on_ground and player.rect.bottom >= len(self.world) * self.tile_size:
            player.rect.bottom = len(self.world) * self.tile_size
            player.velocity.y = 0
            player.is_on_ground = True

    def clamp(self, value: float, lower: float, upper: float) -> float:
        return max(lower, min(value, upper))

    def update_camera(self) -> None:
        world_width_px = len(self.world[0]) * self.tile_size
        world_height_px = len(self.world) * self.tile_size

        target_x = self.player.rect.centerx - WINDOW_WIDTH / 2
        target_y = self.player.rect.centery - WINDOW_HEIGHT / 2

        self.camera.x = self.clamp(target_x, 0, max(0, world_width_px - WINDOW_WIDTH))
        self.camera.y = self.clamp(target_y, 0, max(0, world_height_px - WINDOW_HEIGHT))

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.player.handle_input(event)

    def update(self) -> None:
        dt = self.clock.tick(FPS) / 1000.0
        self._resolve_player_collisions()
        self.player.update(dt)
        self.update_camera()

    def draw(self) -> None:
        self.screen.fill((18, 22, 32))

        start_x = max(0, int(self.camera.x // self.tile_size) - 2)
        end_x = min(len(self.world[0]), int((self.camera.x + WINDOW_WIDTH) // self.tile_size) + 3)
        start_y = max(0, int(self.camera.y // self.tile_size) - 2)
        end_y = min(len(self.world), int((self.camera.y + WINDOW_HEIGHT) // self.tile_size) + 3)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.world[y][x]
                color = self.world_generator.get_color(tile)
                if tile == 9:
                    color = (0, 255, 255)
                rect = pygame.Rect(
                    x * self.tile_size - self.camera.x,
                    y * self.tile_size - self.camera.y,
                    self.tile_size,
                    self.tile_size,
                )
                pygame.draw.rect(self.screen, color, rect)

        self.player.draw(self.screen, self.camera)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
