# Ziemia - Project Development Guide

## Project Overview
Ziemia is a Terraria-style Python game built with Arcade framework. Single-player foundation with future multiplayer expansion capability.

## Technology Stack
- **Framework**: Arcade 2.3.15 (2D game engine)
- **Graphics**: Pyglet 2.1.16 (windowing and rendering)
- **Rendering**: Pillow 12.3.0 (image processing)
- **Linear Algebra**: NumPy 2.5.2
- **Data Format**: JSON (built-in)
- **Persistence**: SQLite3 (built-in)
- **Python**: 3.14+ (tested with Python 3.14.2)

## Current Status: Project Setup Complete ✓
- Virtual environment configured (venv)
- Project structure established
- Core modules scaffolded:
  - Game window (Arcade)
  - Terrain generation (custom procedural implementation)
  - Physics engine (custom SimplePhysicsEngine)
  - Save system (SQLite + JSON)
  - Player entity framework
  - All dependencies installed and verified

## Installation Complete
All required packages have been successfully installed without C++ compilation requirements:
- arcade==2.3.15 ✓
- pyglet==2.1.16 ✓
- pillow==12.3.0 ✓
- numpy==2.5.2 ✓
- pytiled-parser==0.9.4a3 ✓

## Next Steps for Development
1. Implement basic player movement and input handling
2. Create block system and world rendering
3. Add block placement/destruction mechanics
4. Develop inventory system
5. Implement combat/interaction system
6. Add UI and HUD
7. Optional: Integrate Pymunk physics library (requires C++ Build Tools)
8. Optional: Integrate Perlin noise library (requires C++ Build Tools)

## Key Files and Responsibilities
- `main.py`: Application entry point
- `src/game/game.py`: Main game window and render loop
- `src/world/terrain.py`: Procedural generation (custom implementation)
- `src/entities/player.py`: Player character logic
- `src/physics/physics.py`: Custom physics engine
- `src/database/save_manager.py`: Save/load functionality

## Architecture Notes
- Modular design supports easy multiplayer networking addition
- Physics engine decoupled from rendering (custom implementation)
- Database abstraction ready for network serialization
- Asset directories ready for sprite/sound integration
- No external C++ dependencies required for core functionality

## Development Guidelines
- Follow PEP 8 style guide
- Use type hints for function parameters and return types
- Keep modules focused on single responsibility
- Test with `python main.py` to verify changes
- Always use venv for development work
- All core modules have been tested and load successfully

## Running the Game
From the project root directory:
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the game
python main.py
```

Press ESC to exit the game window.

## Building and Extending
- Custom physics implementation allows modification without external compilation
- Terrain generation uses simple procedural methods (easily upgradeable to Perlin noise)
- Save system uses SQLite for persistence and JSON for serialization
- All modules are documented with docstrings and type hints
