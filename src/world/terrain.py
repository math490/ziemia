"""Terrain generation using procedural methods."""

from typing import List
import random


class TerrainGenerator:
    """Generates terrain using procedural generation methods."""

    def __init__(self, seed: int = 0, scale: float = 50.0):
        """
        Initialize terrain generator.
        
        Args:
            seed: Random seed for generation
            scale: Scale of terrain features
        """
        self.seed = seed
        self.scale = scale
        random.seed(seed)

    def generate_terrain(self, width: int, height: int) -> List[List[int]]:
        """
        Generate terrain height map using simple noise.
        
        Args:
            width: Width of terrain map
            height: Height of terrain map
            
        Returns:
            2D list representing terrain heights
        """
        terrain = []
        
        # Create a simple height map using random values
        for y in range(height):
            row = []
            for x in range(width):
                # Use distance-based smoothing for terrain
                # This creates a simple height map
                value = random.randint(50, 200)
                
                # Smooth with neighbors for natural appearance
                if x > 0 and row:
                    value = int((value + row[-1]) / 2)
                
                row.append(value)
            terrain.append(row)
        
        return terrain
