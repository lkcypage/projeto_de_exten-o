import asyncio
import pygame
import random
import unicodedata


# ============================================================
# INICIALIZAÇÃO
# ============================================================

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout 2D - 2 Jogadores")

clock = pygame.time.Clock()


# ============================================================
# CORES
# ============================================================

BLACK = (15, 15, 25)
WHITE = (245, 245, 245)
GRAY = (130, 130, 140)

RED = (230, 70, 70)
ORANGE = (240, 150, 50)
YELLOW = (240, 220, 70)
GREEN = (70, 200, 100)
BLUE = (70, 130, 230)
PURPLE = (170, 80, 220)

DARK_PANEL = (25, 25, 40)
INPUT_COLOR = (245, 245, 245)
INPUT_TEXT = (20, 20, 25)

BRICK_COLORS = [
    RED,
    ORANGE,
    GREEN,
    BLUE,
    PURPLE
]


# ============================================================
# FONTES
# ============================================================

font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
big_font = pygame.font.SysFont("Arial", 42, bold=True)


# ============================================================
# PERGUNTAS EDITÁVEIS
#
# Para pergunta aberta:
#
# {
#     "question": "Quanto é 2 + 2?",
#     "answer": "4"
# }
#
# Para múltipla escolha:
#
# {
#     "question": "Qual é a capital do Brasil?",
#     "options": [
#         "A) São Paulo",
#         "B) Brasília",
#         "C) Rio de Janeiro",
#         "D) Salvador"
#     ],
#     "answer": "B"
# }
#
# Pode misturar os dois tipos.
# ============================================================

QUESTIONS = [

    {
        "question": "Quanto que é 2F em hexadecimal para decimal?",
        "answer": "47"
    },

    {
        "question": "Quanto que corresponde 10101001 de binario para decimal?",
        "answer": "169"
    },

    {
        "question": "100101+101001 em binario?",
        "answer": "1001110"
    },

    {
        "question": "Qual a função do clock da cpu",
        "options": [
            "A) Mudar de estado os registradores",
            "B) Operar o ALU(Aritimetic Logic Unit) e todo barramento",
        ],
        "answer": "B"
    },

    {
        "question": "O ALU tem como operação a soma?(sim/não)",
        "answer": "sim"
    },

    {
        "question": "Quantos bits cabem em 8 bytes?",
        "answer": "32"
    },

    {
        "question": "Qual linguagem usada pela CPU?",
        "answer": "Binario"
    },

    {
        "question": "Função de comparação qual é?",
        "options": [
            "A) XOR",
            "B) AND",
        ],
        "answer": "A"
    },

    {
        "question": "Pode Passar dê o enter",
        "answer": ""
    },

    {
        "question": "Cite as portas mais utilizadas de dois pinos",
        "options": [
            "A) NOT, FLIPFLOP, AND",
            "B) XOR, NOR, AND",
        ],
        "answer": "B"
    }
]


# ============================================================
# NORMALIZAÇÃO DE TEXTO
# ============================================================

def normalize_text(text):

    text = text.strip().lower()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


# ============================================================
# RAQUETE
# ============================================================

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 15
PADDLE_SPEED = 520.0


class Paddle:

    def __init__(self):

        self.rect = pygame.Rect(
            WIDTH // 2 - PADDLE_WIDTH // 2,
            HEIGHT - 50,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )

    def update(self, dt):

        keys = pygame.key.get_pressed()

        direction = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.rect.x += round(
            direction *
            PADDLE_SPEED *
            dt
        )

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self):

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            border_radius=8
        )


# ============================================================
# BOLA
#
# Física:
# - posição Vector2
# - velocidade float
# - delta time
# - colisão por lado
# ============================================================

class Ball:

    def __init__(self):

        self.radius = 7

        self.pos = pygame.Vector2(
            WIDTH / 2,
            HEIGHT - 100
        )

        self.velocity = pygame.Vector2(
            280.0,
            -280.0
        )

        self.max_speed = 650.0

        self.rect = pygame.Rect(
            0,
            0,
            self.radius * 2,
            self.radius * 2
        )

        self.update_rect()

    def update_rect(self):

        self.rect.center = (
            round(self.pos.x),
            round(self.pos.y)
        )

    def reset(self):

        self.pos = pygame.Vector2(
            WIDTH / 2,
            HEIGHT - 100
        )

        direction = random.choice(
            [-1, 1]
        )

        self.velocity = pygame.Vector2(
            280.0 * direction,
            -280.0
        )

        self.update_rect()

    def limit_speed(self):

        speed = self.velocity.length()

        if speed > self.max_speed:

            self.velocity.scale_to_length(
                self.max_speed
            )

    def update(
        self,
        paddle,
        bricks,
        dt
    ):

        # ====================================================
        # MOVIMENTO
        # ====================================================

        self.pos += (
            self.velocity * dt
        )

        # ====================================================
        # PAREDE ESQUERDA
        # ====================================================

        if (
            self.pos.x -
            self.radius <= 0
        ):

            self.pos.x = self.radius

            self.velocity.x = abs(
                self.velocity.x
            )

        # ====================================================
        # PAREDE DIREITA
        # ====================================================

        elif (
            self.pos.x +
            self.radius >= WIDTH
        ):

            self.pos.x = (
                WIDTH -
                self.radius
            )

            self.velocity.x = -abs(
                self.velocity.x
            )

        # ====================================================
        # TETO
        # ====================================================

        if (
            self.pos.y -
            self.radius <= 0
        ):

            self.pos.y = self.radius

            self.velocity.y = abs(
                self.velocity.y
            )

        self.update_rect()

        # ====================================================
        # RAQUETE
        # ====================================================

        if (
            self.rect.colliderect(
                paddle.rect
            )
            and
            self.velocity.y > 0
        ):

            self.pos.y = (
                paddle.rect.top -
                self.radius
            )

            relative_x = (
                self.pos.x -
                paddle.rect.centerx
            ) / (
                paddle.rect.width / 2
            )

            relative_x = max(
                -1,
                min(1, relative_x)
            )

            max_angle = 70

            angle = (
                relative_x *
                max_angle
            )

            direction = pygame.Vector2(
                0,
                -1
            )

            direction = direction.rotate(
                angle
            )

            speed = (
                self.velocity.length()
            )

            self.velocity = (
                direction *
                speed
            )

            self.limit_speed()

            self.update_rect()

        # ====================================================
        # COLISÃO COM BLOCOS
        # ====================================================

        hit_brick = None

        for brick in bricks:

            if self.rect.colliderect(
                brick["rect"]
            ):

                hit_brick = brick
                break

        if hit_brick is not None:

            brick_rect = (
                hit_brick["rect"]
            )

            brick_center = pygame.Vector2(
                brick_rect.centerx,
                brick_rect.centery
            )

            difference = (
                self.pos -
                brick_center
            )

            half_width = (
                brick_rect.width / 2
            )

            half_height = (
                brick_rect.height / 2
            )

            dx = (
                abs(difference.x) /
                half_width
            )

            dy = (
                abs(difference.y) /
                half_height
            )

            # =================================================
            # COLISÃO HORIZONTAL
            # =================================================

            if dx > dy:

                if difference.x > 0:

                    self.pos.x = (
                        brick_rect.right +
                        self.radius
                    )

                    self.velocity.x = abs(
                        self.velocity.x
                    )

                else:

                    self.pos.x = (
                        brick_rect.left -
                        self.radius
                    )

                    self.velocity.x = -abs(
                        self.velocity.x
                    )

            # =================================================
            # COLISÃO VERTICAL
            # =================================================

            else:

                if difference.y > 0:

                    self.pos.y = (
                        brick_rect.bottom +
                        self.radius
                    )

                    self.velocity.y = abs(
                        self.velocity.y
                    )

                else:

                    self.pos.y = (
                        brick_rect.top -
                        self.radius
                    )

                    self.velocity.y = -abs(
                        self.velocity.y
                    )

            self.velocity *= 1.01

            self.limit_speed()

            self.update_rect()

            return hit_brick

        self.update_rect()

        return None

    def draw(self):

        pygame.draw.circle(
            screen,
            WHITE,
            (
                round(self.pos.x),
                round(self.pos.y)
            ),
            self.radius
        )


# ============================================================
# CRIAR BLOCOS
#
# 10 perguntas + blocos normais aleatórios
# ============================================================

def create_bricks():

    bricks = []

    brick_width = 85
    brick_height = 30
    gap = 8

    cols = 8
    rows = 6

    normal_count = random.randint(
        5,
        15
    )

    positions = []

    total_width = (
        cols * brick_width +
        (cols - 1) * gap
    )

    start_x = (
        WIDTH -
        total_width
    ) // 2

    start_y = 80

    for row in range(rows):

        for col in range(cols):

            x = (
                start_x +
                col * (
                    brick_width +
                    gap
                )
            )

            y = (
                start_y +
                row * (
                    brick_height +
                    gap
                )
            )

            positions.append(
                (x, y)
            )

    random.shuffle(
        positions
    )

    # ========================================================
    # 10 PERGUNTAS
    # ========================================================

    for index in range(
        min(10, len(QUESTIONS))
    ):

        if not positions:
            break

        x, y = positions.pop()

        rect = pygame.Rect(
            x,
            y,
            brick_width,
            brick_height
        )

        question_data = QUESTIONS[index]

        brick = {

            "rect": rect,

            "color": YELLOW,

            "type": "question",

            "question":
                question_data["question"],

            "answer":
                question_data["answer"],

            "number":
                index + 1
        }

        # Se existir "options",
        # copia para o bloco.

        if "options" in question_data:

            brick["options"] = (
                question_data["options"]
            )

        bricks.append(
            brick
        )

    # ========================================================
    # BLOCOS NORMAIS
    # ========================================================

    for _ in range(
        normal_count
    ):

        if not positions:
            break

        x, y = positions.pop()

        rect = pygame.Rect(
            x,
            y,
            brick_width,
            brick_height
        )

        bricks.append({

            "rect": rect,

            "color":
                random.choice(
                    BRICK_COLORS
                ),

            "type": "normal",

            "points": 10,

            "number": None
        })

    random.shuffle(
        bricks
    )

    return bricks


# ============================================================
# DESENHAR BLOCOS
# ============================================================

def draw_bricks(bricks):

    for brick in bricks:

        rect = brick["rect"]

        color = brick["color"]

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=6
        )

        highlight = pygame.Rect(
            rect.x + 4,
            rect.y + 3,
            rect.width - 8,
            5
        )

        highlight_color = tuple(
            min(
                255,
                c + 35
            )
            for c in color
        )

        pygame.draw.rect(
            screen,
            highlight_color,
            highlight,
            border_radius=3
        )

        # ====================================================
        # BLOCO DE PERGUNTA
        # ====================================================

        if brick["type"] == "question":

            number = font.render(
                str(brick["number"]),
                True,
                WHITE
            )

            screen.blit(
                number,
                (
                    rect.centerx -
                    number.get_width() // 2,

                    rect.centery -
                    number.get_height() // 2
                )
            )

        # ====================================================
        # BLOCO NORMAL
        # ====================================================

        else:

            pygame.draw.circle(
                screen,
                WHITE,
                rect.center,
                4
            )


# ============================================================
# HUD
# ============================================================

def draw_hud(
    scores,
    lives,
    current_player
):

    color1 = (
        GREEN
        if current_player == 1
        else WHITE
    )

    player1 = font.render(
        f"J1  {scores[1]} pts  "
        f"Vidas: {lives[1]}",
        True,
        color1
    )

    screen.blit(
        player1,
        (15, 18)
    )

    color2 = (
        GREEN
        if current_player == 2
        else WHITE
    )

    player2 = font.render(
        f"J2  {scores[2]} pts  "
        f"Vidas: {lives[2]}",
        True,
        color2
    )

    screen.blit(
        player2,
        (
            WIDTH -
            player2.get_width() -
            15,
            18
        )
    )

    current = small_font.render(
        f"VEZ DO JOGADOR "
        f"{current_player}",
        True,
        YELLOW
    )

    screen.blit(
        current,
        (
            WIDTH // 2 -
            current.get_width() // 2,
            23
        )
    )


# ============================================================
# TELA DE PERGUNTA
# ============================================================

def draw_question_screen(
    question,
    answer,
    message,
    block_number,
    options=None,
    selected_option=None
):

    overlay = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    overlay.set_alpha(235)

    overlay.fill(
        (8, 8, 18)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    # ========================================================
    # PAINEL
    # ========================================================

    panel = pygame.Rect(
        40,
        40,
        WIDTH - 80,
        HEIGHT - 80
    )

    pygame.draw.rect(
        screen,
        DARK_PANEL,
        panel,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        BLUE,
        panel,
        width=2,
        border_radius=15
    )

    # ========================================================
    # TÍTULO
    # ========================================================

    title = big_font.render(
        f"PERGUNTA {block_number}",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2 -
            title.get_width() // 2,
            65
        )
    )

    # ========================================================
    # PERGUNTA
    # ========================================================

    # Quebra de linha simples para perguntas longas

    words = question.split()

    lines = []
    current_line = ""

    for word in words:

        test_line = (
            current_line +
            " " +
            word
        ).strip()

        if font.size(
            test_line
        )[0] <= 650:

            current_line = test_line

        else:

            if current_line:
                lines.append(
                    current_line
                )

            current_line = word

    if current_line:
        lines.append(
            current_line
        )

    question_y = 125

    for line in lines:

        question_surface = font.render(
            line,
            True,
            WHITE
        )

        screen.blit(
            question_surface,
            (
                WIDTH // 2 -
                question_surface.get_width() // 2,
                question_y
            )
        )

        question_y += 30

    # ========================================================
    # MÚLTIPLA ESCOLHA
    # ========================================================

    if options is not None:

        start_y = max(
            190,
            question_y + 15
        )

        for i, option in enumerate(
            options
        ):

            rect = pygame.Rect(
                100,
                start_y + i * 65,
                WIDTH - 200,
                50
            )

            if selected_option == i:

                color = GREEN

            else:

                color = BLUE

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=8
            )

            option_surface = font.render(
                option,
                True,
                WHITE
            )

            screen.blit(
                option_surface,
                (
                    rect.x + 15,
                    rect.y + 12
                )
            )

        instruction = small_font.render(
            "Clique em uma opção ou pressione A, B, C ou D",
            True,
            GRAY
        )

        screen.blit(
            instruction,
            (
                WIDTH // 2 -
                instruction.get_width() // 2,
                500
            )
        )

    # ========================================================
    # PERGUNTA ABERTA
    # ========================================================

    else:

        answer_box = pygame.Rect(
            WIDTH // 2 - 250,
            max(
                220,
                question_y + 20
            ),
            500,
            60
        )

        pygame.draw.rect(
            screen,
            INPUT_COLOR,
            answer_box,
            border_radius=8
        )

        answer_surface = font.render(
            answer,
            True,
            INPUT_TEXT
        )

        screen.blit(
            answer_surface,
            (
                answer_box.x + 15,
                answer_box.y + 16
            )
        )

        # Cursor

        cursor_x = (
            answer_box.x +
            15 +
            answer_surface.get_width()
        )

        pygame.draw.rect(
            screen,
            INPUT_TEXT,
            (
                cursor_x,
                answer_box.y + 13,
                2,
                32
            )
        )

        instruction = small_font.render(
            "Digite a resposta e pressione ENTER",
            True,
            GRAY
        )

        screen.blit(
            instruction,
            (
                WIDTH // 2 -
                instruction.get_width() // 2,
                350
            )
        )

    # ========================================================
    # MENSAGEM
    # ========================================================

    if message:

        message_color = (
            GREEN
            if message == "CORRETO!"
            else RED
        )

        message_surface = font.render(
            message,
            True,
            message_color
        )

        screen.blit(
            message_surface,
            (
                WIDTH // 2 -
                message_surface.get_width() // 2,
                400
            )
        )


# ============================================================
# TELA DE TROCA DE JOGADOR
# ============================================================

def draw_player_change(
    next_player,
    scores,
    reason
):

    overlay = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    overlay.set_alpha(240)

    overlay.fill(BLACK)

    screen.blit(
        overlay,
        (0, 0)
    )

    # ========================================================
    # MOTIVO
    # ========================================================

    reason_surface = font.render(
        reason,
        True,
        RED
    )

    screen.blit(
        reason_surface,
        (
            WIDTH // 2 -
            reason_surface.get_width() // 2,
            120
        )
    )

    # ========================================================
    # PRÓXIMO JOGADOR
    # ========================================================

    title = big_font.render(
        f"VEZ DO JOGADOR {next_player}",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2 -
            title.get_width() // 2,
            180
        )
    )

    # ========================================================
    # PLACAR
    # ========================================================

    score1 = font.render(
        f"Jogador 1: "
        f"{scores[1]} pontos",
        True,
        WHITE
    )

    score2 = font.render(
        f"Jogador 2: "
        f"{scores[2]} pontos",
        True,
        WHITE
    )

    screen.blit(
        score1,
        (
            WIDTH // 2 -
            score1.get_width() // 2,
            280
        )
    )

    screen.blit(
        score2,
        (
            WIDTH // 2 -
            score2.get_width() // 2,
            325
        )
    )

    # ========================================================
    # ENTER
    # ========================================================

    enter = font.render(
        "Pressione ENTER para continuar",
        True,
        GREEN
    )

    screen.blit(
        enter,
        (
            WIDTH // 2 -
            enter.get_width() // 2,
            430
        )
    )


# ============================================================
# TELA FINAL
# ============================================================

def draw_final_result(scores):

    overlay = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    overlay.set_alpha(240)

    overlay.fill(BLACK)

    screen.blit(
        overlay,
        (0, 0)
    )

    # ========================================================
    # TÍTULO
    # ========================================================

    title = big_font.render(
        "FIM DE JOGO",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2 -
            title.get_width() // 2,
            80
        )
    )

    # ========================================================
    # PONTOS
    # ========================================================

    score1 = font.render(
        f"JOGADOR 1: "
        f"{scores[1]} PONTOS",
        True,
        WHITE
    )

    score2 = font.render(
        f"JOGADOR 2: "
        f"{scores[2]} PONTOS",
        True,
        WHITE
    )

    screen.blit(
        score1,
        (
            WIDTH // 2 -
            score1.get_width() // 2,
            200
        )
    )

    screen.blit(
        score2,
        (
            WIDTH // 2 -
            score2.get_width() // 2,
            250
        )
    )

    # ========================================================
    # RESULTADO
    # ========================================================

    if scores[1] > scores[2]:

        result = "JOGADOR 1 VENCEU!"

    elif scores[2] > scores[1]:

        result = "JOGADOR 2 VENCEU!"

    else:

        result = "EMPATE!"

    result_surface = big_font.render(
        result,
        True,
        GREEN
    )

    screen.blit(
        result_surface,
        (
            WIDTH // 2 -
            result_surface.get_width() // 2,
            350
        )
    )

    # ========================================================
    # REINICIAR
    # ========================================================

    restart = font.render(
        "ENTER = jogar novamente",
        True,
        WHITE
    )

    screen.blit(
        restart,
        (
            WIDTH // 2 -
            restart.get_width() // 2,
            450
        )
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # OBJETOS
    # ========================================================

    paddle = Paddle()

    ball = Ball()

    bricks = create_bricks()

    # ========================================================
    # JOGADORES
    # ========================================================

    scores = {
        1: 0,
        2: 0
    }

    lives = {
        1: 3,
        2: 3
    }

    current_player = 1

    # ========================================================
    # ESTADOS
    # ========================================================

    question_active = False

    current_question = None

    answer_text = ""

    answer_message = ""

    selected_option = None

    player_change = False

    change_reason = ""

    game_finished = False

    paused = False

    running = True

    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    while running:

        dt = (
            clock.tick(FPS) /
            1000.0
        )

        # Evita saltos grandes

        dt = min(
            dt,
            0.033
        )

        # ====================================================
        # EVENTOS
        # ====================================================

        for event in pygame.event.get():

            # =================================================
            # FECHAR
            # =================================================

            if event.type == pygame.QUIT:

                running = False

            # =================================================
            # CLIQUE DO MOUSE
            # =================================================

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if (
                    question_active
                    and
                    current_question
                    is not None
                ):

                    options = (
                        current_question.get(
                            "options"
                        )
                    )

                    if options:

                        start_y = max(
                            190,
                            125 + 30 +
                            15
                        )

                        for i in range(
                            len(options)
                        ):

                            rect = pygame.Rect(
                                100,
                                start_y +
                                i * 65,
                                WIDTH - 200,
                                50
                            )

                            if rect.collidepoint(
                                event.pos
                            ):

                                selected_option = i

                                selected_letter = chr(
                                    ord("A") + i
                                )

                                # =================================
                                # CORRETO
                                # =================================

                                if (
                                    selected_letter
                                    ==
                                    current_question[
                                        "answer"
                                    ]
                                ):

                                    if (
                                        current_question
                                        in bricks
                                    ):

                                        bricks.remove(
                                            current_question
                                        )

                                    scores[
                                        current_player
                                    ] += 100

                                    question_active = False

                                    current_question = None

                                    answer_text = ""

                                    selected_option = None

                                    if len(bricks) == 0:

                                        game_finished = True

                                # =================================
                                # ERRADO
                                # =================================

                                else:

                                    question_active = False

                                    current_question = None

                                    answer_text = ""

                                    selected_option = None

                                    player_change = True

                                    change_reason = (
                                        "Você errou a pergunta!"
                                    )

                                break

            # =================================================
            # TECLADO
            # =================================================

            elif event.type == pygame.KEYDOWN:

                # =============================================
                # ESC
                # =============================================

                if event.key == pygame.K_ESCAPE:

                    running = False

                # =============================================
                # PERGUNTA
                # =============================================

                elif question_active:

                    # -----------------------------------------
                    # MÚLTIPLA ESCOLHA
                    # -----------------------------------------

                    options = (
                        current_question.get(
                            "options"
                        )
                    )

                    if options:

                        key_to_index = {

                            pygame.K_a: 0,
                            pygame.K_b: 1,
                            pygame.K_c: 2,
                            pygame.K_d: 3
                        }

                        if event.key in key_to_index:

                            index = (
                                key_to_index[
                                    event.key
                                ]
                            )

                            if index < len(options):

                                selected_option = index

                                selected_letter = chr(
                                    ord("A") + index
                                )

                                # =========================
                                # CORRETO
                                # =========================

                                if (
                                    selected_letter
                                    ==
                                    current_question[
                                        "answer"
                                    ]
                                ):

                                    if (
                                        current_question
                                        in bricks
                                    ):

                                        bricks.remove(
                                            current_question
                                        )

                                    scores[
                                        current_player
                                    ] += 100

                                    question_active = False

                                    current_question = None

                                    answer_text = ""

                                    selected_option = None

                                    if len(bricks) == 0:

                                        game_finished = True

                                # =========================
                                # ERRADO
                                # =========================

                                else:

                                    question_active = False

                                    current_question = None

                                    answer_text = ""

                                    selected_option = None

                                    player_change = True

                                    change_reason = (
                                        "Você errou a pergunta!"
                                    )

                    # -----------------------------------------
                    # PERGUNTA ABERTA
                    # -----------------------------------------

                    else:

                        # BACKSPACE

                        if (
                            event.key ==
                            pygame.K_BACKSPACE
                        ):

                            answer_text = (
                                answer_text[:-1]
                            )

                        # ENTER

                        elif (
                            event.key ==
                            pygame.K_RETURN
                        ):

                            user_answer = (
                                normalize_text(
                                    answer_text
                                )
                            )

                            correct_answer = (
                                normalize_text(
                                    current_question[
                                        "answer"
                                    ]
                                )
                            )

                            # ==============================
                            # CORRETO
                            # ==============================

                            if (
                                user_answer ==
                                correct_answer
                            ):

                                if (
                                    current_question
                                    in bricks
                                ):

                                    bricks.remove(
                                        current_question
                                    )

                                scores[
                                    current_player
                                ] += 100

                                question_active = False

                                current_question = None

                                answer_text = ""

                                selected_option = None

                                if len(bricks) == 0:

                                    game_finished = True

                            # ==============================
                            # ERRADO
                            # ==============================

                            else:

                                question_active = False

                                current_question = None

                                answer_text = ""

                                selected_option = None

                                player_change = True

                                change_reason = (
                                    "Você errou a pergunta!"
                                )

                # =============================================
                # TROCA DE JOGADOR
                # =============================================

                elif player_change:

                    if (
                        event.key ==
                        pygame.K_RETURN
                    ):

                        if current_player == 1:

                            current_player = 2

                        else:

                            current_player = 1

                        # Novo turno começa com 3 vidas

                        lives[
                            current_player
                        ] = 3

                        ball.reset()

                        paddle = Paddle()

                        player_change = False

                        change_reason = ""

                # =============================================
                # FIM DE JOGO
                # =============================================

                elif game_finished:

                    if (
                        event.key ==
                        pygame.K_RETURN
                    ):

                        scores = {
                            1: 0,
                            2: 0
                        }

                        lives = {
                            1: 3,
                            2: 3
                        }

                        current_player = 1

                        bricks = create_bricks()

                        ball = Ball()

                        paddle = Paddle()

                        question_active = False

                        current_question = None

                        answer_text = ""

                        answer_message = ""

                        selected_option = None

                        player_change = False

                        change_reason = ""

                        game_finished = False

                        paused = False

                # =============================================
                # JOGO NORMAL
                # =============================================

                else:

                    if event.key == pygame.K_p:

                        paused = not paused

            # =================================================
            # ENTRADA DE TEXTO
            #
            # IMPORTANTE:
            # usamos TEXTINPUT, não event.unicode.
            # =================================================

            elif event.type == pygame.TEXTINPUT:

                if (
                    question_active
                    and
                    current_question
                    is not None
                    and
                    not current_question.get(
                        "options"
                    )
                ):

                    if len(answer_text) < 40:

                        answer_text += event.text

        # ====================================================
        # FÍSICA
        # ====================================================

        if (
            not game_finished
            and not paused
            and not question_active
            and not player_change
        ):

            paddle.update(dt)

            hit = ball.update(
                paddle,
                bricks,
                dt
            )

            # =================================================
            # BLOCO ATINGIDO
            # =================================================

            if hit is not None:

                # =============================================
                # BLOCO NORMAL
                # =============================================

                if hit["type"] == "normal":

                    if hit in bricks:

                        bricks.remove(
                            hit
                        )

                    scores[
                        current_player
                    ] += hit["points"]

                    if len(bricks) == 0:

                        game_finished = True

                # =============================================
                # BLOCO DE PERGUNTA
                # =============================================

                elif hit["type"] == "question":

                    current_question = hit

                    question_active = True

                    answer_text = ""

                    answer_message = ""

                    selected_option = None

        # ====================================================
        # BOLA CAIU
        # ====================================================

        if (
            not game_finished
            and not paused
            and not question_active
            and not player_change
            and
            ball.pos.y -
            ball.radius > HEIGHT
        ):

            lives[
                current_player
            ] -= 1

            # ================================================
            # ACABARAM AS VIDAS
            # ================================================

            if (
                lives[current_player]
                <= 0
            ):

                player_change = True

                change_reason = (
                    f"Jogador {current_player} "
                    f"perdeu as 3 vidas!"
                )

            # ================================================
            # AINDA TEM VIDA
            # ================================================

            else:

                ball.reset()

                paddle = Paddle()

        # ====================================================
        # DESENHO
        # ====================================================

        screen.fill(
            BLACK
        )

        draw_bricks(
            bricks
        )

        paddle.draw()

        ball.draw()

        draw_hud(
            scores,
            lives,
            current_player
        )

        # ====================================================
        # PAUSA MANUAL
        # ====================================================

        if paused:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(
                180
            )

            overlay.fill(
                BLACK
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            pause_text = big_font.render(
                "PAUSADO",
                True,
                YELLOW
            )

            screen.blit(
                pause_text,
                (
                    WIDTH // 2 -
                    pause_text.get_width() // 2,

                    HEIGHT // 2 -
                    pause_text.get_height() // 2
                )
            )

            pause_info = small_font.render(
                "Pressione P para continuar",
                True,
                WHITE
            )

            screen.blit(
                pause_info,
                (
                    WIDTH // 2 -
                    pause_info.get_width() // 2,
                    HEIGHT // 2 + 45
                )
            )

        # ====================================================
        # PERGUNTA
        # ====================================================

        if (
            question_active
            and
            current_question
            is not None
        ):

            draw_question_screen(

                current_question[
                    "question"
                ],

                answer_text,

                answer_message,

                current_question[
                    "number"
                ],

                current_question.get(
                    "options"
                ),

                selected_option
            )

        # ====================================================
        # TROCA DE JOGADOR
        # ====================================================

        elif player_change:

            next_player = (
                2
                if current_player == 1
                else 1
            )

            draw_player_change(
                next_player,
                scores,
                change_reason
            )

        # ====================================================
        # RESULTADO
        # ====================================================

        elif game_finished:

            draw_final_result(
                scores
            )

        # ====================================================
        # ATUALIZAR TELA
        # ====================================================

        pygame.display.flip()

        # Devolve o controle ao navegador/Pygbag a cada frame.
        await asyncio.sleep(0)

    # ========================================================
    # SAIR
    # ========================================================

    pygame.quit()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())
