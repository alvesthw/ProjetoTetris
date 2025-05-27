import glfw
from OpenGL.GL import *
import random

# Constantes
ROWS, COLS = 20, 10
BLOCK_SIZE = 30
WINDOW_WIDTH, WINDOW_HEIGHT = COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE

# Peças Tetris (formas e rotações)
TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

# Estado do jogo
grid = [[0] * COLS for _ in range(ROWS)]
current_piece = None
piece_pos = [0, 3]  # linha, coluna

def draw_block(x, y, color):
    glColor3fv(color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + BLOCK_SIZE, y)
    glVertex2f(x + BLOCK_SIZE, y + BLOCK_SIZE)
    glVertex2f(x, y + BLOCK_SIZE)
    glEnd()

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col]:
                draw_block(col * BLOCK_SIZE, (ROWS - row - 1) * BLOCK_SIZE, (0.8, 0.2, 0.2))

def draw_piece():
    if not current_piece:
        return
    shape = TETROMINOS[current_piece['type']]
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                draw_block((piece_pos[1] + j) * BLOCK_SIZE, (ROWS - piece_pos[0] - i - 1) * BLOCK_SIZE, (0.2, 0.8, 0.2))

def spawn_piece():
    global current_piece, piece_pos
    piece_type = random.choice(list(TETROMINOS.keys()))
    current_piece = {'type': piece_type}
    piece_pos[:] = [0, 3]

def piece_fits(new_pos):
    shape = TETROMINOS[current_piece['type']]
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                r, c = new_pos[0] + i, new_pos[1] + j
                if r >= ROWS or c < 0 or c >= COLS or (r >= 0 and grid[r][c]):
                    return False
    return True

def fix_piece():
    shape = TETROMINOS[current_piece['type']]
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                r, c = piece_pos[0] + i, piece_pos[1] + j
                grid[r][c] = 1
    clear_lines()
    spawn_piece()

def clear_lines():
    global grid
    grid = [row for row in grid if not all(row)]
    while len(grid) < ROWS:
        grid.insert(0, [0] * COLS)

def update():
    new_pos = [piece_pos[0] + 1, piece_pos[1]]
    if piece_fits(new_pos):
        piece_pos[0] += 1
    else:
        fix_piece()

def key_callback(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_LEFT:
        new_pos = [piece_pos[0], piece_pos[1] - 1]
        if piece_fits(new_pos):
            piece_pos[1] -= 1
    elif key == glfw.KEY_RIGHT:
        new_pos = [piece_pos[0], piece_pos[1] + 1]
        if piece_fits(new_pos):
            piece_pos[1] += 1
    elif key == glfw.KEY_DOWN:
        update()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Tetris 2D", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    spawn_piece()
    last_time = glfw.get_time()
    speed = 0.5

    while not glfw.window_should_close(window):
        now = glfw.get_time()
        if now - last_time > speed:
            update()
            last_time = now

        glClear(GL_COLOR_BUFFER_BIT)
        draw_grid()
        draw_piece()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()