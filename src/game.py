import math

import pygame

from src.config import FPS, TILE_SIZE, TITLE, WINDOW_HEIGHT, WINDOW_WIDTH
from src.entities import Player
from src.world.generation import WorldGenerator
from src.world.world_store import SavedWorld, WorldStore


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.screen_state = "main_menu"
        self.menu_button = pygame.Rect(
            WINDOW_WIDTH // 2 - 170,
            WINDOW_HEIGHT // 2 + 18,
            340,
            64,
        )
        self.exit_button = pygame.Rect(
            WINDOW_WIDTH // 2 - 170,
            WINDOW_HEIGHT // 2 + 96,
            340,
            56,
        )
        self.menu_title_font = pygame.font.SysFont("georgia", 88, bold=True)
        self.menu_button_font = pygame.font.SysFont("georgia", 30, bold=True)
        self.screen_title_font = pygame.font.SysFont("georgia", 48, bold=True)
        self.world_info_font = pygame.font.SysFont("georgia", 20)
        self.world_store = WorldStore()
        self.saved_worlds: list[SavedWorld] = []
        self.world_scroll_offset = 0
        self.visible_world_count = 7
        self.world_list_top = 145
        self.world_row_height = 58
        self.back_button = pygame.Rect(34, 28, 130, 48)
        self.create_world_button = pygame.Rect(WINDOW_WIDTH // 2 - 170, 615, 340, 62)
        self.world_name_input = ""
        self.name_input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 240, 300, 480, 64)
        self.confirm_create_button = pygame.Rect(WINDOW_WIDTH // 2 - 180, 410, 170, 58)
        self.cancel_create_button = pygame.Rect(WINDOW_WIDTH // 2 + 10, 410, 170, 58)

        self.tile_size = TILE_SIZE
        self.world_generator: WorldGenerator | None = None
        self.world: list[list[int]] = []
        self.camera = pygame.Vector2(0, 0)

        self.player = Player(0, 0)
        self.all_sprites: pygame.sprite.Group[Player] = pygame.sprite.Group()
        self.all_sprites.add(self.player)

    def _refresh_saved_worlds(self) -> None:
        self.saved_worlds = self.world_store.list_worlds()
        self.world_scroll_offset = min(
            self.world_scroll_offset,
            max(0, len(self.saved_worlds) - self.visible_world_count),
        )

    def _create_world(self) -> None:
        name = self.world_name_input.strip()
        if not name:
            return

        generator = WorldGenerator(seed=None)
        tiles = generator.generate(240, 80)
        self.world_store.save_world(name, generator.seed, tiles)
        pygame.key.stop_text_input()
        self.world_name_input = ""
        self._refresh_saved_worlds()
        self.screen_state = "world_selection"

    def _enter_world(self, world_id: int) -> None:
        saved_world = self.world_store.load_world(world_id)
        if saved_world is None:
            self._refresh_saved_worlds()
            return

        metadata, self.world = saved_world
        self.world_generator = WorldGenerator(seed=metadata.seed)
        self.player = Player(0, 0)
        self._spawn_player_on_surface()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.camera.update(0, 0)
        self.screen_state = "game"

    def _world_row_rect(self, visible_index: int) -> pygame.Rect:
        return pygame.Rect(
            220,
            self.world_list_top + visible_index * self.world_row_height,
            840,
            50,
        )

    def _delete_world_rect(self, row_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(row_rect.right - 48, row_rect.y + 5, 40, 40)

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
        center_y = len(self.world) // 2
        self.player.rect.center = (
            len(self.world[0]) * self.tile_size // 2,
            len(self.world) * self.tile_size // 2,
        )

        surface_y = len(self.world) - 1
        for y in range(center_y, len(self.world)):
            if self._is_solid_tile(self.world[y][center_x]):
                surface_y = y
                break

        spawn_y = surface_y * self.tile_size - self.player.rect.height
        while spawn_y > 0:
            self.player.rect.y = spawn_y
            left = max(0, self.player.rect.left // self.tile_size)
            right = min(len(self.world[0]) - 1, (self.player.rect.right - 1) // self.tile_size)
            top = self.player.rect.top // self.tile_size
            bottom = (self.player.rect.bottom - 1) // self.tile_size

            if all(
                self.world[tile_y][tile_x] == 9
                for tile_y in range(top, bottom + 1)
                for tile_x in range(left, right + 1)
            ):
                break
            spawn_y -= self.tile_size

        self.player.rect.y = max(0, spawn_y)
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
            tile_x = right
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
            elif self.screen_state == "main_menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu_button.collidepoint(event.pos):
                        self._refresh_saved_worlds()
                        self.screen_state = "world_selection"
                    elif self.exit_button.collidepoint(event.pos):
                        self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._refresh_saved_worlds()
                        self.screen_state = "world_selection"
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            elif self.screen_state == "world_selection":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.screen_state = "main_menu"
                elif event.type == pygame.MOUSEWHEEL:
                    max_offset = max(0, len(self.saved_worlds) - self.visible_world_count)
                    self.world_scroll_offset = max(
                        0,
                        min(max_offset, self.world_scroll_offset - event.y),
                    )
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.collidepoint(event.pos):
                        self.screen_state = "main_menu"
                    elif self.create_world_button.collidepoint(event.pos):
                        self.world_name_input = ""
                        self.screen_state = "world_creation"
                        pygame.key.start_text_input()
                    else:
                        visible_worlds = self.saved_worlds[
                            self.world_scroll_offset : self.world_scroll_offset + self.visible_world_count
                        ]
                        for visible_index, saved_world in enumerate(visible_worlds):
                            row_rect = self._world_row_rect(visible_index)
                            if self._delete_world_rect(row_rect).collidepoint(event.pos):
                                self.world_store.delete_world(saved_world.world_id)
                                self._refresh_saved_worlds()
                                break
                            if row_rect.collidepoint(event.pos):
                                self._enter_world(saved_world.world_id)
                                break
            elif self.screen_state == "world_creation":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.key.stop_text_input()
                        self.screen_state = "world_selection"
                    elif event.key == pygame.K_BACKSPACE:
                        self.world_name_input = self.world_name_input[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._create_world()
                elif event.type == pygame.TEXTINPUT and len(self.world_name_input) < 28:
                    remaining = 28 - len(self.world_name_input)
                    self.world_name_input += event.text[:remaining]
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (
                        self.back_button.collidepoint(event.pos)
                        or self.cancel_create_button.collidepoint(event.pos)
                    ):
                        pygame.key.stop_text_input()
                        self.screen_state = "world_selection"
                    elif self.confirm_create_button.collidepoint(event.pos):
                        self._create_world()
            elif self.screen_state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._refresh_saved_worlds()
                    self.screen_state = "world_selection"
                else:
                    self.player.handle_input(event)

    def update(self) -> None:
        dt = self.clock.tick(FPS) / 1000.0
        self._resolve_player_collisions()
        self.player.update(dt)
        self.update_camera()

    def draw(self) -> None:
        if self.screen_state == "main_menu":
            self._draw_main_menu()
            return
        if self.screen_state == "world_selection":
            self._draw_world_selection()
            return
        if self.screen_state == "world_creation":
            self._draw_world_creation()
            return

        self.screen.fill((18, 22, 32))

        start_x = max(0, int(self.camera.x // self.tile_size) - 2)
        end_x = min(len(self.world[0]), int((self.camera.x + WINDOW_WIDTH) // self.tile_size) + 3)
        start_y = max(0, int(self.camera.y // self.tile_size) - 2)
        end_y = min(len(self.world), int((self.camera.y + WINDOW_HEIGHT) // self.tile_size) + 3)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.world[y][x]
                if self.world_generator is None:
                    raise RuntimeError("O gerador deve estar disponível durante o jogo.")
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

    def _draw_ui_button(
        self,
        rect: pygame.Rect,
        label: str,
        color: tuple[int, int, int] = (119, 79, 48),
    ) -> None:
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        button_color = tuple(min(255, channel + 28) for channel in color) if hovered else color
        pygame.draw.rect(self.screen, (39, 47, 48), rect.move(0, 6))
        pygame.draw.rect(self.screen, (49, 54, 49), rect.inflate(6, 6))
        pygame.draw.rect(self.screen, button_color, rect)
        text = self.menu_button_font.render(label, True, (255, 235, 185))
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw_world_selection(self) -> None:
        self.screen.fill((31, 43, 58))
        pygame.draw.rect(self.screen, (56, 82, 82), (0, 0, WINDOW_WIDTH, 116))
        pygame.draw.rect(self.screen, (79, 121, 91), (0, 116, WINDOW_WIDTH, 8))
        self._draw_ui_button(self.back_button, "Voltar", (83, 83, 68))

        title = self.screen_title_font.render("Mundos", True, (246, 222, 163))
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 76)))

        if not self.saved_worlds:
            empty_message = self.world_info_font.render(
                "Nenhum mundo salvo ainda",
                True,
                (213, 218, 202),
            )
            self.screen.blit(empty_message, empty_message.get_rect(center=(WINDOW_WIDTH // 2, 330)))
        else:
            visible_worlds = self.saved_worlds[
                self.world_scroll_offset : self.world_scroll_offset + self.visible_world_count
            ]
            for visible_index, saved_world in enumerate(visible_worlds):
                row_rect = self._world_row_rect(visible_index)
                pygame.draw.rect(self.screen, (49, 61, 64), row_rect)
                pygame.draw.rect(self.screen, (105, 125, 104), (row_rect.x, row_rect.y, 7, row_rect.height))
                name = self.menu_button_font.render(saved_world.name, True, (244, 231, 190))
                details = self.world_info_font.render(
                    f"{saved_world.width} x {saved_world.height}  |  Seed {saved_world.seed}",
                    True,
                    (181, 197, 184),
                )
                self.screen.blit(name, (row_rect.x + 22, row_rect.y + 3))
                self.screen.blit(details, (row_rect.x + 24, row_rect.y + 31))

                delete_rect = self._delete_world_rect(row_rect)
                pygame.draw.rect(self.screen, (104, 62, 53), delete_rect)
                pygame.draw.line(
                    self.screen,
                    (255, 224, 194),
                    (delete_rect.x + 13, delete_rect.y + 13),
                    (delete_rect.right - 13, delete_rect.bottom - 13),
                    3,
                )
                pygame.draw.line(
                    self.screen,
                    (255, 224, 194),
                    (delete_rect.right - 13, delete_rect.y + 13),
                    (delete_rect.x + 13, delete_rect.bottom - 13),
                    3,
                )

            if len(self.saved_worlds) > self.visible_world_count:
                count = self.world_info_font.render(
                    f"{self.world_scroll_offset + 1}-{min(self.world_scroll_offset + self.visible_world_count, len(self.saved_worlds))} de {len(self.saved_worlds)}",
                    True,
                    (195, 203, 187),
                )
                self.screen.blit(count, count.get_rect(center=(WINDOW_WIDTH // 2, 565)))

        self._draw_ui_button(self.create_world_button, "Criar Mundo", (74, 112, 76))
        pygame.display.flip()

    def _draw_world_creation(self) -> None:
        self.screen.fill((31, 43, 58))
        pygame.draw.rect(self.screen, (56, 82, 82), (0, 0, WINDOW_WIDTH, 116))
        pygame.draw.rect(self.screen, (79, 121, 91), (0, 116, WINDOW_WIDTH, 8))
        self._draw_ui_button(self.back_button, "Voltar", (83, 83, 68))

        title = self.screen_title_font.render("Criar Mundo", True, (246, 222, 163))
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 76)))
        prompt = self.world_info_font.render("Nome do mundo", True, (213, 218, 202))
        self.screen.blit(prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, 270)))

        pygame.draw.rect(self.screen, (24, 34, 42), self.name_input_rect)
        pygame.draw.rect(self.screen, (174, 160, 112), self.name_input_rect, 3)
        name_text = self.menu_button_font.render(self.world_name_input, True, (244, 231, 190))
        self.screen.blit(name_text, (self.name_input_rect.x + 16, self.name_input_rect.y + 14))
        if not self.world_name_input:
            placeholder = self.world_info_font.render("Digite um nome...", True, (128, 146, 141))
            self.screen.blit(placeholder, (self.name_input_rect.x + 16, self.name_input_rect.y + 23))

        self._draw_ui_button(self.confirm_create_button, "Criar", (74, 112, 76))
        self._draw_ui_button(self.cancel_create_button, "Cancelar", (104, 73, 57))
        pygame.display.flip()

    def _draw_main_menu(self) -> None:
        color_stops = (
            (0.0, (31, 43, 72)),
            (0.48, (80, 125, 150)),
            (0.72, (228, 160, 111)),
            (1.0, (91, 126, 116)),
        )
        for y in range(0, WINDOW_HEIGHT, 4):
            position = y / WINDOW_HEIGHT
            color = color_stops[-1][1]
            for index in range(len(color_stops) - 1):
                start, start_color = color_stops[index]
                end, end_color = color_stops[index + 1]
                if start <= position <= end:
                    blend = (position - start) / (end - start)
                    color = tuple(
                        int(first + (second - first) * blend)
                        for first, second in zip(start_color, end_color)
                    )
                    break
            pygame.draw.rect(self.screen, color, (0, y, WINDOW_WIDTH, 4))

        pygame.draw.rect(self.screen, (255, 213, 139), (930, 205, 76, 76))
        pygame.draw.rect(self.screen, (255, 226, 164), (946, 221, 44, 44))

        for cloud_x, cloud_y, scale in ((155, 170, 1), (790, 285, 2), (1070, 125, 1)):
            cloud_color = (207, 218, 210)
            pygame.draw.rect(self.screen, cloud_color, (cloud_x, cloud_y, 64 * scale, 16 * scale))
            pygame.draw.rect(self.screen, cloud_color, (cloud_x + 16 * scale, cloud_y - 16 * scale, 32 * scale, 16 * scale))
            pygame.draw.rect(self.screen, cloud_color, (cloud_x + 48 * scale, cloud_y - 8 * scale, 24 * scale, 8 * scale))

        pygame.draw.polygon(
            self.screen,
            (69, 105, 119),
            ((0, 480), (150, 355), (260, 445), (405, 325), (590, 480), (760, 375), (940, 485), (1100, 350), (1280, 475), (1280, 560), (0, 560)),
        )
        pygame.draw.polygon(
            self.screen,
            (74, 121, 113),
            ((0, 485), (185, 410), (355, 480), (540, 390), (750, 488), (950, 405), (1120, 480), (1280, 420), (1280, 560), (0, 560)),
        )

        for tree_x, tree_y, size in ((86, 397, 1), (1130, 390, 1), (1190, 430, 0.75)):
            trunk_width = int(18 * size)
            trunk_height = int(82 * size)
            pygame.draw.rect(self.screen, (91, 65, 52), (tree_x, tree_y, trunk_width, trunk_height))
            leaf_size = int(32 * size)
            for leaf_x, leaf_y in ((-leaf_size, 0), (0, -leaf_size), (leaf_size, 0), (0, leaf_size)):
                pygame.draw.rect(
                    self.screen,
                    (58, 119, 82),
                    (tree_x + trunk_width // 2 + leaf_x - leaf_size // 2, tree_y + leaf_y - leaf_size // 2, leaf_size, leaf_size),
                )
            pygame.draw.rect(self.screen, (91, 151, 91), (tree_x, tree_y, trunk_width, int(12 * size)))

        ground_top = 520
        for block_x in range(0, WINDOW_WIDTH, 32):
            surface_y = ground_top + int(10 * math.sin(block_x / 115))
            pygame.draw.rect(self.screen, (89, 158, 91), (block_x, surface_y, 32, 14))
            pygame.draw.rect(self.screen, (114, 84, 60), (block_x, surface_y + 14, 32, WINDOW_HEIGHT - surface_y))
            pygame.draw.line(self.screen, (88, 69, 55), (block_x, surface_y + 30), (block_x + 31, surface_y + 30), 1)

        self._draw_ui_button(self.menu_button, "Jogar Solo")
        self._draw_ui_button(self.exit_button, "Sair", (104, 62, 53))

        title = self.menu_title_font.render("Ziemia", True, (246, 222, 163))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 205))
        self.screen.blit(title, title_rect.move(0, 7))
        for offset in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            self.screen.blit(title, title_rect.move(*offset))
        self.screen.blit(title, title_rect)
        pygame.draw.rect(self.screen, (238, 190, 115), (WINDOW_WIDTH // 2 - 72, 268, 144, 3))
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            if self.screen_state != "game":
                self.clock.tick(FPS)
            else:
                self.update()
            self.draw()

        pygame.quit()
