from __future__ import annotations

import pygame


class PlayerState:
    """Classe base para os estados do personagem."""

    def __init__(self, player: "Player") -> None:
        self.player = player

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_input(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class IdleState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "idle"

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
            self.player.state_machine.replace(MoveState(self.player))
        elif event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE) and self.player.is_on_ground:
            self.player.state_machine.replace(JumpState(self.player))
        elif event.key == pygame.K_j:
            self.player.state_machine.replace(AttackState(self.player))
        elif event.key == pygame.K_b:
            self.player.state_machine.replace(BuildState(self.player))

    def update(self, dt: float) -> None:
        self.player.velocity.x = 0
        if not self.player.is_on_ground:
            self.player.state_machine.replace(FallState(self.player))


class MoveState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "run"

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE) and self.player.is_on_ground:
            self.player.state_machine.replace(JumpState(self.player))
        elif event.key == pygame.K_j:
            self.player.state_machine.replace(AttackState(self.player))

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction += 1

        self.player.facing = 1 if direction >= 0 else -1
        self.player.velocity.x = direction * self.player.speed

        if direction == 0:
            self.player.state_machine.replace(IdleState(self.player))
            return

        if not self.player.is_on_ground:
            self.player.state_machine.replace(FallState(self.player))


class JumpState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "jump"
        self.player.velocity.y = -self.player.jump_force
        self.player.is_on_ground = False

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction += 1
        self.player.facing = 1 if direction >= 0 else -1
        self.player.velocity.x = direction * self.player.speed

        if self.player.velocity.y >= 0:
            self.player.state_machine.replace(FallState(self.player))


class FallState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "fall"

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction += 1
        self.player.facing = 1 if direction >= 0 else -1
        self.player.velocity.x = direction * self.player.speed

        if self.player.is_on_ground:
            if direction != 0:
                self.player.state_machine.replace(MoveState(self.player))
            else:
                self.player.state_machine.replace(IdleState(self.player))


class AttackState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "attack"
        self.player.attack_timer = 0.25

    def update(self, dt: float) -> None:
        self.player.attack_timer -= dt
        if self.player.attack_timer <= 0:
            if self.player.is_on_ground:
                if self.player.velocity.x != 0:
                    self.player.state_machine.replace(MoveState(self.player))
                else:
                    self.player.state_machine.replace(IdleState(self.player))
            else:
                self.player.state_machine.replace(FallState(self.player))


class BuildState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "build"
        self.player.build_timer = 0.30

    def update(self, dt: float) -> None:
        self.player.build_timer -= dt
        if self.player.build_timer <= 0:
            if self.player.is_on_ground:
                if self.player.velocity.x != 0:
                    self.player.state_machine.replace(MoveState(self.player))
                else:
                    self.player.state_machine.replace(IdleState(self.player))
            else:
                self.player.state_machine.replace(FallState(self.player))


class HurtState(PlayerState):
    def enter(self) -> None:
        self.player.animation = "hurt"
        self.player.invulnerability = 0.5

    def update(self, dt: float) -> None:
        self.player.invulnerability -= dt
        if self.player.invulnerability <= 0:
            if self.player.is_on_ground:
                if self.player.velocity.x != 0:
                    self.player.state_machine.replace(MoveState(self.player))
                else:
                    self.player.state_machine.replace(IdleState(self.player))
            else:
                self.player.state_machine.replace(FallState(self.player))


class PlayerStateMachine:
    """Máquina de estados em pilha, com polimorfismo por herança."""

    def __init__(self, player: "Player") -> None:
        self.player = player
        self.stack: list[PlayerState] = []

    def push(self, state: PlayerState):
        if self.stack:
            self.stack[-1].exit()
        self.stack.append(state)
        state.enter()

    def pop(self):
        if not self.stack:
            return
        self.stack[-1].exit()
        self.stack.pop()
        if self.stack:
            self.stack[-1].enter()

    def replace(self, state: PlayerState):
        if self.stack:
            self.stack[-1].exit()
            self.stack.pop()
        self.stack.append(state)
        state.enter()

    def current(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def handle_input(self, event: pygame.event.Event):
        if current := self.current():
            current.handle_input(event)

    def update(self, dt: float):
        if current := self.current():
            current.update(dt)

    def draw(self, surface: pygame.Surface):
        if current := self.current():
            current.draw(surface)


class Player(pygame.sprite.Sprite):
    """Jogador do mundo Ziemia."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.image = pygame.Surface((28, 42))
        self.image.fill((59, 130, 246))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.prev_rect = self.rect.copy()

        self.speed = 240.0
        self.jump_force = 520.0
        self.gravity = 1200.0
        self.facing = 1
        self.animation = "idle"
        self.attack_timer = 0.0
        self.build_timer = 0.0
        self.invulnerability = 0.0

        self.velocity = pygame.Vector2(0, 0)
        self.is_on_ground = False

        self.state_machine = PlayerStateMachine(self)
        self.state_machine.replace(IdleState(self))

    def handle_input(self, event: pygame.event.Event) -> None:
        self.state_machine.handle_input(event)

    def update(self, dt: float) -> None:
        self.prev_rect = self.rect.copy()
        self.state_machine.update(dt)

        if not self.is_on_ground:
            self.velocity.y += self.gravity * dt
        else:
            self.velocity.y = 0

        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        self.velocity.y = min(self.velocity.y, 900)

        if self.invulnerability > 0:
            self.invulnerability = max(0, self.invulnerability - dt)

    def draw(self, surface: pygame.Surface, camera: pygame.Vector2 | None = None) -> None:
        render_pos = self.rect.topleft
        if camera is not None:
            render_pos = (self.rect.x - camera.x, self.rect.y - camera.y)

        draw_rect = self.rect.copy()
        draw_rect.topleft = render_pos
        pygame.draw.rect(surface, (59, 130, 246), draw_rect)

    def take_damage(self) -> None:
        self.state_machine.replace(HurtState(self))
