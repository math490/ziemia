# Ziemia

Jogo 2D tipo sandbox inspirado em Terraria, em desenvolvimento com Python e Pygame.

## Estrutura do projeto

- `main.py`: ponto de entrada do jogo
- `src/`: código principal do jogo
  - `config.py`: configurações gerais
  - `game.py`: loop principal e estado do jogo
  - `entities/`: entidades do mundo
  - `ui/`: interface do jogador
  - `world/`: gerador de mapa, biomas e mundo
- `assets/`: imagens, tiles, efeitos e sons
- `saves/`: arquivos salvos do jogador

## Como rodar

1. Crie a virtualenv
2. Instale as dependências
3. Execute:

```bash
python main.py
```

## Stack

- Python 3.12+
- Pygame
- NumPy
- Noise (opcional para geração procedural)
