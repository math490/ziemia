"""Physics engine wrapper for game objects."""

from typing import Dict, List, Tuple


class PhysicsBody:
    """Simple physics body for game objects."""

    def __init__(self, x: float, y: float, width: float, height: float, 
                 mass: float = 1.0, is_static: bool = False):
        """
        Initialize physics body.
        
        Args:
            x, y: Position
            width, height: Dimensions
            mass: Mass of the body (ignored if static)
            is_static: Whether this body is affected by gravity
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mass = mass if not is_static else float('inf')
        self.is_static = is_static
        
        # Velocity
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Acceleration
        self.accel_x = 0.0
        self.accel_y = 0.0


class SimplePhysicsEngine:
    """Simple physics engine for the game."""

    def __init__(self, gravity: float = 9.81):
        """
        Initialize physics engine.
        
        Args:
            gravity: Gravity acceleration value
        """
        self.gravity = gravity
        self.bodies: List[PhysicsBody] = []

    def add_body(self, body: PhysicsBody):
        """
        Add a body to the physics engine.
        
        Args:
            body: PhysicsBody to add
        """
        self.bodies.append(body)

    def remove_body(self, body: PhysicsBody):
        """
        Remove a body from the physics engine.
        
        Args:
            body: PhysicsBody to remove
        """
        if body in self.bodies:
            self.bodies.remove(body)

    def step(self, delta_time: float):
        """
        Step the physics simulation.
        
        Args:
            delta_time: Time step in seconds
        """
        for body in self.bodies:
            if not body.is_static:
                # Apply gravity
                body.accel_y = -self.gravity
                
                # Update velocity
                body.velocity_x += body.accel_x * delta_time
                body.velocity_y += body.accel_y * delta_time
                
                # Update position
                body.x += body.velocity_x * delta_time
                body.y += body.velocity_y * delta_time
