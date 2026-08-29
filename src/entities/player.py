"""Player entity class."""


class Player:
    """Represents the player character."""

    def __init__(self, x: float, y: float):
        """
        Initialize player.
        
        Args:
            x: X position
            y: Y position
        """
        self.x = x
        self.y = y
        self.width = 32
        self.height = 64
        
        # Player stats
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = 260.0
        self.jump_strength = 520.0
        self.gravity = 1200.0
        self.on_ground = False

    def move(self, direction: float):
        """Set horizontal movement direction."""
        self.velocity_x = direction * self.speed

    def jump(self):
        """Jump if the player is on the ground."""
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False

    def update(self, delta_time: float, ground_y: float, max_x: float):
        """Update player state."""
        self.velocity_y -= self.gravity * delta_time
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        floor_y = ground_y + self.height / 2
        if self.y <= floor_y:
            self.y = floor_y
            self.velocity_y = 0.0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.x < self.width / 2:
            self.x = self.width / 2
        if self.x > max_x - self.width / 2:
            self.x = max_x - self.width / 2

    def take_damage(self, amount: int):
        """
        Take damage.
        
        Args:
            amount: Damage amount
        """
        self.health = max(0, self.health - amount)

    def heal(self, amount: int):
        """
        Heal the player.
        
        Args:
            amount: Healing amount
        """
        self.health = min(self.max_health, self.health + amount)
