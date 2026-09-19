# Ziemia - A Terraria-style Adventure Game

Ziemia is a Python-based sandbox adventure game inspired by Terraria, created using the Arcade framework. The game features procedural world generation, custom physics simulation, and persistent game saves. The project is designed as a single-player experience with architecture ready for future multiplayer expansion.

## Features

- **Procedural World Generation**: Simple procedural terrain generation (upgradeable to Perlin noise)
- **Custom Physics Simulation**: Lightweight physics engine for realistic movement and interactions
- **Persistent Saves**: SQLite-based save system with JSON serialization
- **Single-player Experience**: Full campaign with progression systems
- **Future Multiplayer**: Modular architecture ready for network expansion
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## Project Structure

```
Ziemia/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .github/
│   └── copilot-instructions.md  # Development guide
├── .vscode/
│   └── settings.json      # IDE configuration
├── src/
│   ├── game/              # Core game logic
│   │   ├── game.py       # Main game window (1280x720, 60 FPS)
│   │   └── __init__.py
│   ├── world/             # World generation
│   │   ├── terrain.py    # Procedural terrain generation
│   │   └── __init__.py
│   ├── entities/          # Game entities
│   │   ├── player.py     # Player class with health/mana
│   │   └── __init__.py
│   ├── physics/           # Physics simulation
│   │   ├── physics.py    # Custom physics engine
│   │   └── __init__.py
│   └── database/          # Data persistence
│       ├── save_manager.py # SQLite save/load system
│       └── __init__.py
├── assets/
│   ├── images/            # Sprite sheets, textures (placeholder)
│   └── sounds/            # Audio files (placeholder)
├── data/                  # Save files and game data
└── venv/                  # Python virtual environment
```

## Dependencies

### Core Requirements
- **arcade** (3.3.3): Modern Python game framework (2D graphics, input, timing)
- **pyglet** (2.1.16): Windowing and rendering backend
- **pillow** (12.3.0): Image processing and sprite handling
- **numpy** (2.5.2): Numerical operations
- **pytiled-parser** (2.2.9): Tile map parsing

### Optional (Not included to avoid C++ compilation)
- **pymunk**: Physics simulation library (requires Microsoft C++ Build Tools)
- **noise**: Perlin noise generation (requires Microsoft C++ Build Tools)

Custom implementations of both physics and terrain generation are included in the project to eliminate compilation requirements on Windows.

## Installation & Setup

### Prerequisites
- Python 3.8+ (tested with Python 3.14.2)
- pip package manager

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

All packages install via binary wheels with no C++ compilation required.

## Running the Game

```bash
python main.py
```

### Controls
- **A/D** or **Left/Right**: Movement
- **W/Up/Space**: Jump
- **Left Mouse**: Break and collect a nearby block
- **Right Mouse**: Place the selected block
- **F4**: Toggle fullscreen
- **+/-**: Zoom camera in or out
- **ESC**: Exit the game

The window is resizable. The camera follows the player smoothly through the
expanded world, and terrain outside the camera view is culled to reduce draw
work. The outer ten blocks on each side are kept outside the playable and
visible area. The world uses a block grid, and the selected hotbar item is
consumed when a valid block is placed. Only placed solid blocks support
vertical landing, horizontal blocking, and head collision when jumping;
background terrain and grass are visual/non-solid.

### Planned Controls
- **WASD**: Movement
- **Space**: Jump
- **Left Mouse**: Mine/Interact
- **Right Mouse**: Place block
- **E**: Open inventory
- **ESC**: Pause menu

## Development Status

### Completed ✓
- Virtual environment setup
- Project structure scaffolding
- Core modules implemented:
  - Game window with Arcade framework
  - Custom SimplePhysicsEngine
  - Procedural terrain generator
  - Player entity with health/mana system
  - SQLite-based save system with JSON serialization
- All dependencies installed and verified
- Cross-platform compatibility (Windows, macOS, Linux)

### In Progress
- Player movement and input handling
- Block system and world rendering
- Basic UI/HUD

### Planned
- Block placement/destruction mechanics
- Inventory system
- Combat system
- NPC system
- Environmental hazards
- Multiplayer networking (Phase 3)

## Code Architecture

### Game Loop
The game uses Arcade's standard game loop pattern:
- `setup()`: Initialize game state
- `on_draw()`: Render frame
- `on_update()`: Update game logic
- `on_key_press/release()`: Handle input
- `on_mouse_press()`: Handle mouse input

### Physics System
Custom `SimplePhysicsEngine` provides:
- Body management (static and dynamic)
- Gravity simulation
- Velocity and acceleration tracking
- Collision-ready structure (extensible)

### Save System
`SaveManager` uses SQLite with:
- Player data (JSON serialized)
- World data (JSON serialized)
- Inventory tracking
- Timestamp metadata

## Extending the Game

### Adding New Features
1. Create new module in appropriate `src/` subdirectory
2. Implement with type hints and docstrings
3. Test module imports from `main.py`
4. Update this README

### Upgrading Physics (Optional)
To use Pymunk physics library:
```bash
pip install pymunk
```
Then modify `src/physics/physics.py` to use Pymunk backend.

### Adding Perlin Noise (Optional)
To use noise library for better terrain:
```bash
pip install noise
```
Then modify `src/world/terrain.py` to use noise generation.

Note: Both optional dependencies require Microsoft C++ Build Tools on Windows. See [C++ Build Tools installation](https://visualstudio.microsoft.com/visual-cpp-build-tools/) for details.

## Performance

- **Target**: 60 FPS at 1280x720
- **Physics**: Fixed timestep physics updates
- **Rendering**: Batched sprite rendering via Arcade
- **Memory**: Efficient entity management with object pooling potential

## Troubleshooting

### ModuleNotFoundError for arcade
Ensure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Import errors for custom modules
Verify `src/` directory is in Python path. Check `main.py` includes:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

### Game window won't open
Check Pyglet/display compatibility. Try setting:
```bash
export SDL_VIDEODRIVER=dummy  # macOS/Linux testing
```

## Contributing

This is an active personal project. Contributions welcome via pull requests.

## License

MIT License - Feel free to use and modify for personal or commercial projects.

## Roadmap

### Phase 1: Foundation (Current - 50%)
Single-player gameplay fundamentals

### Phase 2: Content (Planned)
Expanded game systems, NPCs, progression

### Phase 3: Multiplayer (Future)
Network architecture, server/client implementation

---

**Last Updated**: August 28, 2026
**Python Version**: 3.14.2
**Arcade Version**: 3.3.3
