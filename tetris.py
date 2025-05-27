import glfw
from OpenGL.GL import *
import random

# Constantes
LINHAS, COLUNAS = 20, 10
TAMANHO_BLOCO = 30
LARGURA_JANELA, ALTURA_JANELA = COLUNAS * TAMANHO_BLOCO * 2, LINHAS * TAMANHO_BLOCO  # duas áreas lado a lado

# Peças do Tetris
PEÇAS_TETRIS = {
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

def rotacionar(formato):
    return [list(linha) for linha in zip(*formato[::-1])]

class Jogador:
    def __init__(self, deslocamento_x, teclas):
        self.deslocamento_x = deslocamento_x  # deslocamento horizontal na tela para desenhar
        self.teclas = teclas  # dicionário com as teclas (esq, dir, baixo, rotacionar)
        self.grade = [[0] * COLUNAS for _ in range(LINHAS)]
        self.peca_atual = None
        self.pos_peca = [0, 3]
        self.gerar_peca()

    def gerar_peca(self):
        self.peca_atual = {'tipo': random.choice(list(PEÇAS_TETRIS.keys())), 'formato': None}
        self.peca_atual['formato'] = PEÇAS_TETRIS[self.peca_atual['tipo']]
        self.pos_peca = [0, 3]

    def peca_cabe(self, pos, formato):
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l, c = pos[0] + i, pos[1] + j
                    if l >= LINHAS or c < 0 or c >= COLUNAS or (l >= 0 and self.grade[l][c]):
                        return False
        return True

    def fixar_peca(self):
        formato = self.peca_atual['formato']
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l, c = self.pos_peca[0] + i, self.pos_peca[1] + j
                    self.grade[l][c] = 1
        self.remover_linhas()
        self.gerar_peca()

    def remover_linhas(self):
        self.grade = [linha for linha in self.grade if not all(linha)]
        while len(self.grade) < LINHAS:
            self.grade.insert(0, [0] * COLUNAS)

    def atualizar(self):
        nova_pos = [self.pos_peca[0] + 1, self.pos_peca[1]]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[0] += 1
        else:
            self.fixar_peca()

    def mover_esquerda(self):
        nova_pos = [self.pos_peca[0], self.pos_peca[1] - 1]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[1] -= 1

    def mover_direita(self):
        nova_pos = [self.pos_peca[0], self.pos_peca[1] + 1]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[1] += 1

    def mover_baixo(self):
        self.atualizar()

    def rotacionar_peca(self):
        novo_formato = rotacionar(self.peca_atual['formato'])
        if self.peca_cabe(self.pos_peca, novo_formato):
            self.peca_atual['formato'] = novo_formato

    def desenhar_bloco(self, x, y, cor):
        glColor3fv(cor)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + TAMANHO_BLOCO, y)
        glVertex2f(x + TAMANHO_BLOCO, y + TAMANHO_BLOCO)
        glVertex2f(x, y + TAMANHO_BLOCO)
        glEnd()

    def desenhar_grade(self):
        for l in range(LINHAS):
            for c in range(COLUNAS):
                if self.grade[l][c]:
                    self.desenhar_bloco(self.deslocamento_x + c * TAMANHO_BLOCO, (LINHAS - l - 1) * TAMANHO_BLOCO, (0.8, 0.2, 0.2))

    def desenhar_peca(self):
        formato = self.peca_atual['formato']
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    self.desenhar_bloco(self.deslocamento_x + (self.pos_peca[1] + j) * TAMANHO_BLOCO, (LINHAS - self.pos_peca[0] - i - 1) * TAMANHO_BLOCO, (0.2, 0.8, 0.2))

# Configuração dos jogadores
# Jogador 1 usa setas: esquerda, direita, baixo, cima (rotacionar)
teclas_jogador1 = {
    'esquerda': glfw.KEY_LEFT,
    'direita': glfw.KEY_RIGHT,
    'baixo': glfw.KEY_DOWN,
    'rotacionar': glfw.KEY_UP
}
# Jogador 2 usa WASD: A, D, S, W (rotacionar)
teclas_jogador2 = {
    'esquerda': glfw.KEY_A,
    'direita': glfw.KEY_D,
    'baixo': glfw.KEY_S,
    'rotacionar': glfw.KEY_W
}

jogadores = [
    Jogador(0, teclas_jogador1),
    Jogador(COLUNAS * TAMANHO_BLOCO, teclas_jogador2)
]

def tecla_callback(janela, tecla, scancode, acao, mods):
    if acao != glfw.PRESS:
        return
    for jogador in jogadores:
        if tecla == jogador.teclas['esquerda']:
            jogador.mover_esquerda()
        elif tecla == jogador.teclas['direita']:
            jogador.mover_direita()
        elif tecla == jogador.teclas['baixo']:
            jogador.mover_baixo()
        elif tecla == jogador.teclas['rotacionar']:
            jogador.rotacionar_peca()

def principal():
    if not glfw.init():
        return
    janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, "Tetris Multijogador Local", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)
    glfw.set_key_callback(janela, tecla_callback)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, LARGURA_JANELA, 0, ALTURA_JANELA, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    tempo_anterior = glfw.get_time()
    velocidade = 0.5

    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        if agora - tempo_anterior > velocidade:
            for jogador in jogadores:
                jogador.atualizar()
            tempo_anterior = agora

        glClear(GL_COLOR_BUFFER_BIT)
        for jogador in jogadores:
            jogador.desenhar_grade()
            jogador.desenhar_peca()
        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    principal()