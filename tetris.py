import glfw
from OpenGL.GL import *
import random

# Constantes
LINHAS, COLUNAS = 20, 10
TAMANHO_BLOCO = 30
LARGURA_JANELA, ALTURA_JANELA = COLUNAS * TAMANHO_BLOCO, LINHAS * TAMANHO_BLOCO

# Peças do Tetris (formatos)
PECAS_TETRIS = {
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
grade = [[0] * COLUNAS for _ in range(LINHAS)]
peca_atual = None
posicao_peca = [0, 3]  # linha, coluna


def desenhar_bloco(x, y, cor):
    glColor3fv(cor)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + TAMANHO_BLOCO, y)
    glVertex2f(x + TAMANHO_BLOCO, y + TAMANHO_BLOCO)
    glVertex2f(x, y + TAMANHO_BLOCO)
    glEnd()

def desenhar_grade():
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            if grade[linha][coluna]:
                desenhar_bloco(coluna * TAMANHO_BLOCO, (LINHAS - linha - 1) * TAMANHO_BLOCO, (0.8, 0.2, 0.2))

def desenhar_peca():
    if not peca_atual:
        return
    forma = peca_atual['forma']
    for i, linha in enumerate(forma):
        for j, val in enumerate(linha):
            if val:
                desenhar_bloco((posicao_peca[1] + j) * TAMANHO_BLOCO, (LINHAS - posicao_peca[0] - i - 1) * TAMANHO_BLOCO, (0.2, 0.8, 0.2))

def gerar_nova_peca():
    global peca_atual, posicao_peca
    tipo = random.choice(list(PECAS_TETRIS.keys()))
    forma = PECAS_TETRIS[tipo]
    peca_atual = {'tipo': tipo, 'forma': forma}
    posicao_peca[:] = [0, 3]




def rotacionar(matriz):
    return [list(linha) for linha in zip(*matriz[::-1])]

def peca_cabe(nova_pos, nova_forma):
    for i, linha in enumerate(nova_forma):
        for j, val in enumerate(linha):
            if val:
                r, c = nova_pos[0] + i, nova_pos[1] + j
                if r >= LINHAS or c < 0 or c >= COLUNAS or (r >= 0 and grade[r][c]):
                    return False
    return True

def fixar_peca():
    forma = peca_atual['forma']
    for i, linha in enumerate(forma):
        for j, val in enumerate(linha):
            if val:
                r, c = posicao_peca[0] + i, posicao_peca[1] + j
                grade[r][c] = 1
    limpar_linhas()
    gerar_nova_peca()

def limpar_linhas():
    global grade
    grade = [linha for linha in grade if not all(linha)]
    while len(grade) < LINHAS:
        grade.insert(0, [0] * COLUNAS)

def atualizar():
    nova_pos = [posicao_peca[0] + 1, posicao_peca[1]]
    if peca_cabe(nova_pos, peca_atual['forma']):
        posicao_peca[0] += 1
    else:
        fixar_peca()

def tratar_teclas(janela, tecla, scancode, acao, mods):
    if acao != glfw.PRESS:
        return

    if tecla == glfw.KEY_LEFT:
        nova_pos = [posicao_peca[0], posicao_peca[1] - 1]
        if peca_cabe(nova_pos, peca_atual['forma']):
            posicao_peca[1] -= 1
    elif tecla == glfw.KEY_RIGHT:
        nova_pos = [posicao_peca[0], posicao_peca[1] + 1]
        if peca_cabe(nova_pos, peca_atual['forma']):
            posicao_peca[1] += 1
    elif tecla == glfw.KEY_DOWN:
        atualizar()
    elif tecla == glfw.KEY_UP:
        nova_forma = rotacionar(peca_atual['forma'])
        if peca_cabe(posicao_peca, nova_forma):
            peca_atual['forma'] = nova_forma

def principal():
    if not glfw.init():
        return
    janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, "Tetris 2D", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)
    glfw.set_key_callback(janela, tratar_teclas)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, LARGURA_JANELA, 0, ALTURA_JANELA, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    gerar_nova_peca()
    tempo_anterior = glfw.get_time()
    velocidade = 0.5

    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        if agora - tempo_anterior > velocidade:
            atualizar()
            tempo_anterior = agora

        glClear(GL_COLOR_BUFFER_BIT)
        desenhar_grade()
        desenhar_peca()
        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    principal()
