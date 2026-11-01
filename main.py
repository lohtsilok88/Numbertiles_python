import random
import pygame
import sys

# Number Tiles - Pygame edition
# Rules preserved from the supplied HTML:
# - Choose a 3x3, 4x4, or 5x5 board.
# - Allowed maximum values depend on board size.
# - Clicking a tile subtracts 1 from its row and column (not twice
#   from the intersection), wrapping around modulo max_value + 1.
# - Solve the board by making every tile zero.
# - A generated board is guaranteed solvable in exactly `size` moves.

pygame.init()

WIDTH, HEIGHT = 650, 760
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Number Tiles")
CLOCK = pygame.time.Clock()

BG = (15, 23, 42)
PANEL = (30, 41, 59)
TILE = (30, 41, 59)
TILE_BORDER = (71, 85, 105)
BLUE = (59, 130, 246)
AMBER = (245, 158, 11)
RED = (239, 68, 68)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
GREEN = (16, 185, 129)
DARK = (15, 23, 42)

FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL = pygame.font.SysFont("arial", 18)
TINY = pygame.font.SysFont("arial", 15)
BIG = pygame.font.SysFont("arial", 32, bold=True)

size = 3
max_value = 4
board = []
initial_board = []
history = []
status = ""
solved = False

def allowed_max_values(n):
    return {3: (3, 4), 4: (3, 5), 5: (4, 6)}[n]

def clamp_max_value():
    global max_value
    low, high = allowed_max_values(size)
    max_value = max(low, min(high, max_value))

def apply_move(target, row, col, solving=True):
    """Apply one tile move to target in place."""
    modulus = max_value + 1
    delta = -1 if solving else 1

    for c in range(size):
        target[row][c] = (target[row][c] + delta) % modulus

    for r in range(size):
        if r != row:
            target[r][col] = (target[r][col] + delta) % modulus

def generate_level():
    """Create a non-zero board from exactly `size` reversible moves.

    Starting with all zeroes, apply the inverse of the player's move
    `size` times. Therefore replaying those same positions solves it.
    """
    global board, initial_board, history, status, solved

    attempts = 0
    while True:
        candidate = [[0 for _ in range(size)] for _ in range(size)]
        solution_moves = [
            (random.randrange(size), random.randrange(size))
            for _ in range(size)
        ]

        # The generation operation is the inverse of a player move.
        for r, c in solution_moves:
            apply_move(candidate, r, c, solving=False)

        if all(value != 0 for row in candidate for value in row):
            break

        attempts += 1
        # The random sequence has a good chance of producing a valid
        # board. This fallback is only a safety net for unusual cases.
        if attempts > 100000:
            candidate = [[0 for _ in range(size)] for _ in range(size)]
            solution_moves = [(i, i) for i in range(size)]
            for r, c in solution_moves:
                apply_move(candidate, r, c, solving=False)
            if not all(value != 0 for row in candidate for value in row):
                # A valid board can still be made by trying random sequences.
                attempts = 0

    board = [row[:] for row in candidate]
    initial_board = [row[:] for row in candidate]
    history = []
    status = ""
    solved = False

def reset_board():
    global board, history, status, solved
    if not initial_board:
        return
    board = [row[:] for row in initial_board]
    history = []
    status = ""
    solved = False

def undo():
    global board, status, solved
    if history:
        board = history.pop()
        status = ""
        solved = all(v == 0 for row in board for v in row)

def change_size(direction):
    global size, max_value
    size = max(3, min(5, size + direction))
    clamp_max_value()
    generate_level()

def change_max(direction):
    global max_value
    low, high = allowed_max_values(size)
    max_value = max(low, min(high, max_value + direction))
    generate_level()

def draw_text(text, font, color, center):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect(center=center)
    SCREEN.blit(surface, rect)

def draw_button(rect, label, color, enabled=True):
    fill = color if enabled else (75, 85, 99)
    pygame.draw.rect(SCREEN, fill, rect, border_radius=8)
    draw_text(label, SMALL, WHITE if enabled else MUTED, rect.center)

def tile_rect(row, col):
    board_width = 440
    gap = 8
    tile_size = (board_width - gap * (size - 1)) // size
    left = (WIDTH - board_width) // 2
    top = 270
    return pygame.Rect(
        left + col * (tile_size + gap),
        top + row * (tile_size + gap),
        tile_size,
        tile_size
    )

def draw():
    SCREEN.fill(BG)

    draw_text("NUMBER TILES", BIG, WHITE, (WIDTH // 2, 45))
    draw_text("Make every tile zero to solve the puzzle.", SMALL, MUTED,
              (WIDTH // 2, 83))

    panel = pygame.Rect(95, 115, 460, 130)
    pygame.draw.rect(SCREEN, PANEL, panel, border_radius=14)
    pygame.draw.rect(SCREEN, (51, 65, 85), panel, 2, border_radius=14)

    draw_text("Grid size", SMALL, WHITE, (185, 145))
    draw_button(pygame.Rect(245, 128, 42, 34), "−", BLUE, size > 3)
    draw_text(size, FONT, WHITE, (315, 145))
    draw_button(pygame.Rect(345, 128, 42, 34), "+", BLUE, size < 5)

    draw_text("Maximum tile value", SMALL, WHITE, (185, 195))
    draw_button(pygame.Rect(245, 178, 42, 34), "−", BLUE,
                max_value > allowed_max_values(size)[0])
    draw_text(max_value, FONT, WHITE, (315, 195))
    draw_button(pygame.Rect(345, 178, 42, 34), "+", BLUE,
                max_value < allowed_max_values(size)[1])

    draw_button(pygame.Rect(405, 135, 125, 65), "Generate", GREEN)

    draw_text(f"Goal: solve in exactly {size} moves", SMALL, MUTED,
              (WIDTH // 2, 263))

    if status:
        draw_text(status, FONT, GREEN if solved else AMBER,
                  (WIDTH // 2, 680))

    for r in range(size):
        for c in range(size):
            rect = tile_rect(r, c)
            value = board[r][c]
            color = DARK if value == 0 else TILE
            pygame.draw.rect(SCREEN, color, rect, border_radius=7)
            pygame.draw.rect(SCREEN, TILE_BORDER, rect, 2, border_radius=7)
            draw_text(value, FONT, MUTED if value == 0 else WHITE, rect.center)

    draw_button(pygame.Rect(145, 625, 155, 42), "Undo", AMBER,
                bool(history) and not solved)
    draw_button(pygame.Rect(350, 625, 155, 42), "Reset", RED,
                bool(history) and not solved)

    draw_text("Click a tile: subtract 1 across its row and column.",
              TINY, MUTED, (WIDTH // 2, 715))
    pygame.display.flip()

def handle_click(pos):
    global board, status, solved

    # Grid and max-value controls
    if pygame.Rect(245, 128, 42, 34).collidepoint(pos) and size > 3:
        change_size(-1)
        return
    if pygame.Rect(345, 128, 42, 34).collidepoint(pos) and size < 5:
        change_size(1)
        return
    low, high = allowed_max_values(size)
    if pygame.Rect(245, 178, 42, 34).collidepoint(pos) and max_value > low:
        change_max(-1)
        return
    if pygame.Rect(345, 178, 42, 34).collidepoint(pos) and max_value < high:
        change_max(1)
        return
    if pygame.Rect(405, 135, 125, 65).collidepoint(pos):
        generate_level()
        return
    if pygame.Rect(145, 625, 155, 42).collidepoint(pos):
        undo()
        return
    if pygame.Rect(350, 625, 155, 42).collidepoint(pos):
        reset_board()
        return

    if solved:
        return

    for r in range(size):
        for c in range(size):
            if tile_rect(r, c).collidepoint(pos):
                history.append([row[:] for row in board])
                apply_move(board, r, c, solving=True)
                solved = all(value == 0 for row in board for value in row)
                status = "SOLVED!" if solved else ""
                return

def main():
    generate_level()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_u:
                    undo()
                elif event.key == pygame.K_r:
                    reset_board()
                elif event.key == pygame.K_n:
                    generate_level()

        draw()
        CLOCK.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

