import glfw
from OpenGL.GL import *
import random
import math
import pygame
from OpenGL.GLUT import *

# Constants
LINHAS, COLUNAS = 20, 10
TAMANHO_BLOCO = 30
LARGURA_JANELA, ALTURA_JANELA = COLUNAS * TAMANHO_BLOCO * 2, LINHAS * TAMANHO_BLOCO
estado_jogo = "jogando"
VELOCIDADE_INICIAL = 0.8
VELOCIDADE_MINIMA = 0.2
INCREMENTO_VELOCIDADE = 0.06
TEMPO_ACELERACAO = 30

# Tetris pieces
PEÇAS_TETRIS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# Player colors
CORES_POR_JOGADOR = [
    {  # Player 1
        'I': (0.0, 1.0, 1.0),
        'O': (1.0, 1.0, 0.0),
        'T': (0.0, 1.0, 0.0),
        'S': (0.0, 0.5, 1.0),
        'Z': (1.0, 0.0, 0.0),
        'J': (0.0, 0.0, 1.0),
        'L': (1.0, 0.5, 0.0),
    },
    {  # Player 2
        'I': (0.2, 0.8, 1.0),
        'O': (1.0, 0.8, 0.3),
        'T': (0.8, 0.0, 0.8),
        'S': (0.0, 1.0, 0.6),
        'Z': (1.0, 0.4, 0.4),
        'J': (0.4, 0.4, 1.0),
        'L': (1.0, 0.7, 0.3),
    }
]

# Control keys
teclas_jogador1 = {
    'esquerda': glfw.KEY_A,
    'direita': glfw.KEY_D,
    'baixo': glfw.KEY_S,
    'rotacionar': glfw.KEY_W
}

teclas_jogador2 = {
    'esquerda': glfw.KEY_LEFT,
    'direita': glfw.KEY_RIGHT,
    'baixo': glfw.KEY_DOWN,
    'rotacionar': glfw.KEY_UP
}

# Initialize pygame and sounds
def inicializar_sons():
    pygame.init()
    pygame.mixer.init()
    
    try:
        som_fixar = pygame.mixer.Sound("sons/fixa.wav")
        som_linha = pygame.mixer.Sound("sons/fixa.wav")
        som_fundo = pygame.mixer.Sound("sons/fundo.ogg")
        som_gameover = pygame.mixer.Sound("sons/gameover.wav")
        pygame.mixer.Sound.play(som_fundo, loops=-1)
    except pygame.error as e:
        print(f"Erro ao carregar som: {e}. Usando fallback silencioso.")
        empty_sound = pygame.mixer.Sound(pygame.sndarray.make_sound([[0]]))
        som_fixar = som_linha = som_fundo = som_gameover = empty_sound
    
    return som_fixar, som_linha, som_fundo, som_gameover

som_fixar, som_linha, som_fundo, som_gameover = inicializar_sons()

class Jogador:
    def __init__(self, deslocamento_x, teclas, id_jogador):
        self.grade = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.peca_atual = None
        self.pos_peca = [0, 3]
        self.teclas = teclas
        self.deslocamento_x = deslocamento_x
        self.id_jogador = id_jogador
        self.perdeu_jogo = False
        self.velocidade = VELOCIDADE_INICIAL
        self.nivel = 1
        self.ultimo_movimento_peca = 0
        self.gerar_peca()

    def perdeu(self):
        return any(cell is not None for cell in self.grade[0])

    def gerar_peca(self):
        tipo = random.choice(list(PEÇAS_TETRIS.keys()))
        formato = PEÇAS_TETRIS[tipo]
        cor = CORES_POR_JOGADOR[self.id_jogador][tipo]
        self.pos_peca = [0, 3]
        
        if not self.peca_cabe(self.pos_peca, formato):
            self.perdeu_jogo = True
            pygame.mixer.Sound.play(som_gameover)
            return False
            
        self.peca_atual = {'tipo': tipo, 'formato': formato, 'cor': cor}
        return True

    def peca_cabe(self, pos, formato):
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l, c = pos[0] + i, pos[1] + j
                    if (l >= LINHAS or c < 0 or c >= COLUNAS or 
                        (l >= 0 and self.grade[l][c] is not None)):
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
        return self.gerar_peca()

    def remover_linhas(self):
        linhas_antes = len(self.grade)
        self.grade = [linha for linha in self.grade if any(cell is None for cell in linha)]
        linhas_removidas = linhas_antes - len(self.grade)
        
        if linhas_removidas > 0:
            pygame.mixer.Sound.play(som_linha)
            self.velocidade = max(VELOCIDADE_MINIMA, 
                                self.velocidade - (linhas_removidas * INCREMENTO_VELOCIDADE))
            self.nivel += linhas_removidas
            
        while len(self.grade) < LINHAS:
            self.grade.insert(0, [None] * COLUNAS)

    def obter_blocos_peca(self):
        blocos = []
        formato = self.peca_atual['formato']
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    l = self.pos_peca[0] + i
                    c = self.pos_peca[1] + j
                    blocos.append((l, c))
        return blocos

    def atualizar(self):
        if self.perdeu_jogo:
            return False

        nova_pos = [self.pos_peca[0] + 1, self.pos_peca[1]]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[0] += 1
            return True
        else:
            return self.fixar_peca()

    def mover_esquerda(self):
        if self.perdeu_jogo: return
        nova_pos = [self.pos_peca[0], self.pos_peca[1] - 1]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[1] -= 1

    def mover_direita(self):
        if self.perdeu_jogo: return
        nova_pos = [self.pos_peca[0], self.pos_peca[1] + 1]
        if self.peca_cabe(nova_pos, self.peca_atual['formato']):
            self.pos_peca[1] += 1

    def mover_baixo(self):
        if self.perdeu_jogo: return
        self.atualizar()

    def rotacionar_peca(self):
        if self.perdeu_jogo: return
        novo_formato = rotacionar(self.peca_atual['formato'])
        test_offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for offset_r, offset_c in test_offsets:
            test_pos = [self.pos_peca[0] + offset_r, self.pos_peca[1] + offset_c]
            if self.peca_cabe(test_pos, novo_formato):
                self.pos_peca = test_pos
                self.peca_atual['formato'] = novo_formato
                break

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
        if self.peca_atual is None:
            return

        formato = self.peca_atual['formato']
        cor = self.peca_atual['cor']
        for i, linha in enumerate(formato):
            for j, val in enumerate(linha):
                if val:
                    self.desenhar_bloco(self.deslocamento_x + (self.pos_peca[1] + j) * TAMANHO_BLOCO,
                                      (LINHAS - self.pos_peca[0] - i - 1) * TAMANHO_BLOCO, cor)

def rotacionar(formato):
    return [list(linha) for linha in zip(*formato[::-1])]

def desenhar_grade_animada():
    glLineWidth(1)
    glBegin(GL_LINES)
    for x in range(0, LARGURA_JANELA, TAMANHO_BLOCO):
        glVertex2f(x, 0)
        glVertex2f(x, ALTURA_JANELA)
    for y in range(0, ALTURA_JANELA, TAMANHO_BLOCO):
        glVertex2f(0, y)
        glVertex2f(LARGURA_JANELA, y)
    
    glColor3f(1.0, 1.0, 1.0)
    meio = LARGURA_JANELA // 2
    glVertex2f(meio, 0)
    glVertex2f(meio, ALTURA_JANELA)
    glEnd()

def tecla_callback(janela, tecla, scancode, acao, mods):
    if acao != glfw.PRESS:
        return

    for jogador in jogadores:
        if jogador.perdeu_jogo:
            continue
        
        if tecla == jogador.teclas['esquerda']:
            jogador.mover_esquerda()
        elif tecla == jogador.teclas['direita']:
            jogador.mover_direita()
        elif tecla == jogador.teclas['baixo']:
            jogador.mover_baixo()
        elif tecla == jogador.teclas['rotacionar']:
            jogador.rotacionar_peca()

def tela_inicial():
    largura, altura = 400, 300
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Tela Inicial - Tetris")
    fonte = pygame.font.Font(None, 32)
    relogio = pygame.time.Clock()

    nome1, nome2 = "", ""
    ativo1, ativo2 = False, False

    input_box1 = pygame.Rect(100, 60, 200, 32)
    input_box2 = pygame.Rect(100, 120, 200, 32)
    botao_start = pygame.Rect(150, 200, 100, 40)

    rodando = True
    while rodando:
        tela.fill((30, 30, 30))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(evento.pos):
                    ativo1 = True
                    ativo2 = False
                elif input_box2.collidepoint(evento.pos):
                    ativo2 = True
                    ativo1 = False
                elif botao_start.collidepoint(evento.pos):
                    if nome1.strip() != "" and nome2.strip() != "":
                        rodando = False
            if evento.type == pygame.KEYDOWN:
                if ativo1:
                    if evento.key == pygame.K_BACKSPACE:
                        nome1 = nome1[:-1]
                    else:
                        nome1 += evento.unicode
                elif ativo2:
                    if evento.key == pygame.K_BACKSPACE:
                        nome2 = nome2[:-1]
                    else:
                        nome2 += evento.unicode

        cor_box1 = (255, 255, 255) if ativo1 else (150, 150, 150)
        cor_box2 = (255, 255, 255) if ativo2 else (150, 150, 150)
        pygame.draw.rect(tela, cor_box1, input_box1, 2)
        pygame.draw.rect(tela, cor_box2, input_box2, 2)
        pygame.draw.rect(tela, (0, 200, 0), botao_start)

        texto_input1 = fonte.render(nome1, True, (255, 255, 255))
        texto_input2 = fonte.render(nome2, True, (255, 255, 255))
        tela.blit(texto_input1, (input_box1.x + 5, input_box1.y + 5))
        tela.blit(texto_input2, (input_box2.x + 5, input_box2.y + 5))

        label1 = fonte.render("Jogador 1:", True, (200, 200, 200))
        label2 = fonte.render("Jogador 2:", True, (200, 200, 200))
        tela.blit(label1, (input_box1.x, input_box1.y - 25))
        tela.blit(label2, (input_box2.x, input_box2.y - 25))

        start_txt = fonte.render("Start", True, (0, 0, 0))
        tela.blit(start_txt, (botao_start.x + 20, botao_start.y + 10))

        pygame.display.flip()
        relogio.tick(30)

    return nome1.strip(), nome2.strip()

def mostrar_tela_gameover(nome1, nome2, jogadores):
    largura, altura = 400, 300
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Game Over")
    fonte = pygame.font.Font(None, 36)
    fonte_pequena = pygame.font.Font(None, 24)
    relogio = pygame.time.Clock()

    perdedor = "Nenhum"
    vencedor = "Nenhum"

    if jogadores[0].perdeu_jogo and jogadores[1].perdeu_jogo:
        perdedor = f"{nome1} e {nome2}"
        vencedor = "Empate (ou ambos perderam)"
    elif jogadores[0].perdeu_jogo:
        perdedor = nome1
        vencedor = nome2
    elif jogadores[1].perdeu_jogo:
        perdedor = nome2
        vencedor = nome1
    else:
        perdedor = "Um jogador"
        vencedor = "Outro jogador"

    rodando = True
    while rodando:
        tela.fill((30, 30, 30))

        texto = fonte.render("GAME OVER", True, (255, 0, 0))
        tela.blit(texto, (largura//2 - texto.get_width()//2, 50))

        texto_perdedor = fonte_pequena.render(f"{perdedor} perdeu!", True, (255, 0, 0))
        texto_vencedor = fonte_pequena.render(f"{vencedor} venceu!", True, (0, 255, 0))

        tela.blit(texto_perdedor, (largura//2 - texto_perdedor.get_width()//2, 120))
        tela.blit(texto_vencedor, (largura//2 - texto_vencedor.get_width()//2, 160))

        botao_sair = pygame.Rect(largura//2 - 50, 220, 100, 40)
        pygame.draw.rect(tela, (255, 0, 0), botao_sair)
        texto_sair = fonte_pequena.render("Sair", True, (255, 255, 255))
        tela.blit(texto_sair, (botao_sair.x + 25, botao_sair.y + 10))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_sair.collidepoint(evento.pos):
                    rodando = False

        pygame.display.flip()
        relogio.tick(30)

    pygame.quit()
    exit()

def principal(nome1, nome2):
    global estado_jogo, jogadores

    if not glfw.init():
        print("Erro: Falha ao inicializar GLFW!")
        return

    janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, "Tetris Multijogador Local", None, None)
    if not janela:
        glfw.terminate()
        print("Erro: Falha ao criar a janela GLFW!")
        return

    glfw.make_context_current(janela)
    glutInit()
    glfw.set_key_callback(janela, tecla_callback)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, LARGURA_JANELA, 0, ALTURA_JANELA, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    tempo_inicial_do_jogo = glfw.get_time()
    for jogador in jogadores:
        jogador.ultimo_movimento_peca = tempo_inicial_do_jogo 

    ultimo_aumento_dificuldade = tempo_inicial_do_jogo

    while not glfw.window_should_close(janela):
        tempo_atual = glfw.get_time()
        
        if tempo_atual - ultimo_aumento_dificuldade > TEMPO_ACELERACAO:
            for jogador in jogadores:
                nova_velocidade = max(VELOCIDADE_MINIMA, jogador.velocidade - 0.05) 
                jogador.velocidade = nova_velocidade
            ultimo_aumento_dificuldade = tempo_atual

        # Verifica se algum jogador perdeu
        for jogador in jogadores:
            if not jogador.perdeu_jogo:  # Apenas jogadores ativos devem atualizar
                if tempo_atual - jogador.ultimo_movimento_peca > jogador.velocidade:
                    if not jogador.atualizar():
                        if jogador.perdeu():
                            jogador.perdeu_jogo = True
                            pygame.mixer.Sound.play(som_gameover)

                    jogador.ultimo_movimento_peca = tempo_atual


        # Agora, verifica se **todos** os jogadores perderam antes de encerrar o jogo
        if any(j.perdeu_jogo for j in jogadores):
            estado_jogo = "fim"

        if estado_jogo == "fim":
            glfw.destroy_window(janela)
            mostrar_tela_gameover(nome1, nome2, jogadores)
            glfw.terminate()
            return

        # Renderização da tela
        tempo_render = glfw.get_time()
        r = (math.sin(tempo_render * 0.4) + 1) / 2 * 0.3 + 0.1
        g = (math.sin(tempo_render * 0.6 + 2) + 1) / 2 * 0.3 + 0.1
        b = (math.sin(tempo_render * 0.8 + 4) + 1) / 2 * 0.3 + 0.1
        glClearColor(r, g, b, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        
        brilho = (math.sin(tempo_render * 2) + 1) / 2 * 0.4 + 0.2
        glColor3f(brilho, brilho, brilho)
        desenhar_grade_animada()

        for jogador in jogadores:
            jogador.desenhar_grade()
            if not jogador.perdeu_jogo:
                jogador.desenhar_peca()

        # Exibição dos nomes dos jogadores
        glColor3f(1, 1, 1)
        for i, jogador in enumerate(jogadores):
            glRasterPos2f(jogador.deslocamento_x + (COLUNAS * TAMANHO_BLOCO * 0.15), ALTURA_JANELA - 30) 
            nome_display = nome1 if i == 0 else nome2
            texto_display = f"{nome_display} (Nível: {jogador.nivel})"
            for c in texto_display:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    estado_jogo = "jogando"
    nome1, nome2 = tela_inicial()

    jogadores = [
        Jogador(0, teclas_jogador1, 0),
        Jogador(COLUNAS * TAMANHO_BLOCO, teclas_jogador2, 1)
    ]
    principal(nome1, nome2) 