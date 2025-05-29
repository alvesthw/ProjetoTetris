import glfw
from OpenGL.GL import *
import random
import math
import pygame

# Inicialização
pygame.init()
pygame.mixer.init()

# Sons
som_fixar = pygame.mixer.Sound("sons/fixa.wav")
som_linha = pygame.mixer.Sound("sons/fixa.wav")
som_fundo = pygame.mixer.Sound("sons/fundo.ogg")
som_gameover = pygame.mixer.Sound("sons/gameover.wav")
pygame.mixer.Sound.play(som_fundo, loops=-1)

# Constantes
LINHAS, COLUNAS = 20, 10
TAMANHO_BLOCO = 30
LARGURA_JANELA, ALTURA_JANELA = COLUNAS * TAMANHO_BLOCO * 2, LINHAS * TAMANHO_BLOCO
jogo_ativo = True

# Peças
PEÇAS_TETRIS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# Cores diferentes para cada jogador
CORES_POR_JOGADOR = [
    {  # Jogador 1
        'I': (0.0, 1.0, 1.0),
        'O': (1.0, 1.0, 0.0),
        'T': (0.0, 1.0, 0.0),
        'S': (0.0, 0.5, 1.0),
        'Z': (1.0, 0.0, 0.0),
        'J': (0.0, 0.0, 1.0),
        'L': (1.0, 0.5, 0.0),
    },
    {  # Jogador 2
        'I': (0.2, 0.8, 1.0),
        'O': (1.0, 0.8, 0.3),
        'T': (0.8, 0.0, 0.8),
        'S': (0.0, 1.0, 0.6),
        'Z': (1.0, 0.4, 0.4),
        'J': (0.4, 0.4, 1.0),
        'L': (1.0, 0.7, 0.3),
    }
]

def rotacionar(formato):
    return [list(linha) for linha in zip(*formato[::-1])]

class Jogador:
    def __init__(self, deslocamento_x, teclas, id_jogador):
        self.grade = [[None] * COLUNAS for _ in range(LINHAS)]
        self.peca_atual = None
        self.pos_peca = [0, 3]
        self.teclas = teclas
        self.deslocamento_x = deslocamento_x
        self.id_jogador = id_jogador
        self.gerar_peca()

    def gerar_peca(self):
        global jogo_ativo
        tipo = random.choice(list(PEÇAS_TETRIS.keys()))
        formato = PEÇAS_TETRIS[tipo]
        cor = CORES_POR_JOGADOR[self.id_jogador][tipo]
        nova_pos = [0, 3]

        if not self.peca_cabe(nova_pos, formato) and jogo_ativo:
            jogo_ativo = False
            pygame.mixer.Sound.play(som_gameover)
            perdedor = f"Jogador {self.id_jogador + 1}"
            vencedor = f"Jogador {2 if self.id_jogador == 0 else 1}"
            print(f"\n🎮 GAME OVER! {perdedor} perdeu!")
            print(f"🏆 {vencedor.upper()} VENCEU!")
            glfw.set_window_should_close(glfw.get_current_context(), True)
            return

        self.peca_atual = {'tipo': tipo, 'formato': formato, 'cor': cor}
        self.pos_peca = nova_pos

    def peca_cabe(self, pos, formato):
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l, c = pos[0] + i, pos[1] + j
                    if l >= LINHAS or c < 0 or c >= COLUNAS or (l >= 0 and self.grade[l][c] is not None):
                        return False
        return True

    def fixar_peca(self):
        formato = self.peca_atual['formato']
        cor = self.peca_atual['cor']

        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l, c = self.pos_peca[0] + i, self.pos_peca[1] + j
                    if 0 <= l < LINHAS and 0 <= c < COLUNAS:
                        self.grade[l][c] = cor

        pygame.mixer.Sound.play(som_fixar)
        self.remover_linhas()
        self.gerar_peca()

    def remover_linhas(self):
        nova_grade = [linha for linha in self.grade if any(cor is None for cor in linha)]
        if len(nova_grade) < LINHAS:
            pygame.mixer.Sound.play(som_linha)
        while len(nova_grade) < LINHAS:
            nova_grade.insert(0, [None] * COLUNAS)
        self.grade = nova_grade

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
                cor = self.grade[l][c]
                if cor:
                    self.desenhar_bloco(self.deslocamento_x + c * TAMANHO_BLOCO,
                                        (LINHAS - l - 1) * TAMANHO_BLOCO, cor)

    def desenhar_peca(self):
        formato = self.peca_atual['formato']
        cor = self.peca_atual['cor']
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    self.desenhar_bloco(self.deslocamento_x + (self.pos_peca[1] + j) * TAMANHO_BLOCO,
                                        (LINHAS - self.pos_peca[0] - i - 1) * TAMANHO_BLOCO, cor)

def desenhar_grade_animada():
    glLineWidth(1)
    glBegin(GL_LINES)
    for x in range(0, LARGURA_JANELA, TAMANHO_BLOCO):
        glVertex2f(x, 0)
        glVertex2f(x, ALTURA_JANELA)
    for y in range(0, ALTURA_JANELA, TAMANHO_BLOCO):
        glVertex2f(0, y)
        glVertex2f(LARGURA_JANELA, y)
    glColor3f(1, 1, 1)
    meio = LARGURA_JANELA // 2
    glVertex2f(meio, 0)
    glVertex2f(meio, ALTURA_JANELA)
    glEnd()

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

        tempo = glfw.get_time()
        r = (math.sin(tempo * 0.4) + 1) / 2 * 0.3 + 0.1
        g = (math.sin(tempo * 0.6 + 2) + 1) / 2 * 0.3 + 0.1
        b = (math.sin(tempo * 0.8 + 4) + 1) / 2 * 0.3 + 0.1
        glClearColor(r, g, b, 1)

        glClear(GL_COLOR_BUFFER_BIT)
        brilho = (math.sin(tempo * 2) + 1) / 2 * 0.4 + 0.2
        glColor3f(brilho, brilho, brilho)
        desenhar_grade_animada()

        for jogador in jogadores:
            jogador.desenhar_grade()
            jogador.desenhar_peca()

        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()

# Teclas
teclas_jogador1 = {
    'esquerda': glfw.KEY_LEFT,
    'direita': glfw.KEY_RIGHT,
    'baixo': glfw.KEY_DOWN,
    'rotacionar': glfw.KEY_UP
}

teclas_jogador2 = {
    'esquerda': glfw.KEY_A,
    'direita': glfw.KEY_D,
    'baixo': glfw.KEY_S,
    'rotacionar': glfw.KEY_W
}

jogadores = [
    Jogador(0, teclas_jogador1, 0),
    Jogador(COLUNAS * TAMANHO_BLOCO, teclas_jogador2, 1)
]

if __name__ == "__main__":
    principal()
