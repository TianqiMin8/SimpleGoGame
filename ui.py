import pygame
import sys
from core_game import Game, BLACK, WHITE, EMPTY

BOARD_SIZE = 9
CELL_SIZE = 60
MARGIN = 40

BG_COLOR = (220, 179, 92)
LINE_COLOR = (0, 0, 0)
BLACK_COLOR = (20, 20, 20)
WHITE_COLOR = (240, 240, 240)

SIDEBAR_WIDTH = 200
WIDTH = (BOARD_SIZE - 1) * CELL_SIZE + MARGIN * 2 + SIDEBAR_WIDTH
HEIGHT = (BOARD_SIZE - 1) * CELL_SIZE + MARGIN * 2


class GoUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wang Go Game")

        self.game = Game(BOARD_SIZE)
        self.sidebar_x = (BOARD_SIZE - 1) * CELL_SIZE + MARGIN * 2
        self.pass_button = pygame.Rect(self.sidebar_x + 40, HEIGHT - 80, 120, 40)
        self.font = pygame.font.SysFont("Arial", 20)

    def board_to_pixel(self, r, c):
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        return x, y

    def pixel_to_board(self, x, y):
        c = round((x - MARGIN) / CELL_SIZE)
        r = round((y - MARGIN) / CELL_SIZE)
        return r, c

    def draw(self):
        self.screen.fill(BG_COLOR)

        # draw grids
        for i in range(BOARD_SIZE):
            pygame.draw.line(
                self.screen, LINE_COLOR,
                self.board_to_pixel(i, 0),
                self.board_to_pixel(i, BOARD_SIZE - 1)
            )
            pygame.draw.line(
                self.screen, LINE_COLOR,
                self.board_to_pixel(0, i),
                self.board_to_pixel(BOARD_SIZE - 1, i)
            )
        star_points = [
            (2, 2), (2, 6),
            (4, 4),
            (6, 2), (6, 6)
        ]

        for r, c in star_points:
            x, y = self.board_to_pixel(r, c)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 4)

        # draw stones
        radius = CELL_SIZE // 2 - 4

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                val = self.game.board.get(r, c)
                if val == EMPTY:
                    continue

                pos = self.board_to_pixel(r, c)
                color = BLACK_COLOR if val == BLACK else WHITE_COLOR
                pygame.draw.circle(self.screen, color, pos, radius)

                if self.game.last_move and self.game.last_move == (r, c):
                    mark_color = (255, 255, 255) if color == BLACK else (0, 0, 0)
                    
                    mark_radius = max(2, radius // 3)
                    
                    pygame.draw.circle(self.screen, mark_color, pos, mark_radius)
        
        # Side bar
        pygame.draw.rect(self.screen, (50, 50, 60), (self.sidebar_x, 0, SIDEBAR_WIDTH, HEIGHT))

        # current stage
        turn = "Black" if self.game.current_player == BLACK else "White"
        text = self.font.render(f"Turn: {turn}", True, (255, 255, 255))
        self.screen.blit(text, (self.sidebar_x + 20, 40))

        # Game Over
        if self.game.game_over:
            over = self.font.render("GAME OVER", True, (255, 100, 100))
            self.screen.blit(over, (self.sidebar_x + 20, 80))
        

        b = self.game.captured[BLACK]
        w = self.game.captured[WHITE]

        text_b = self.font.render(f"Black captured: {b}", True, (255,255,255))
        text_w = self.font.render(f"White captured: {w}", True, (255,255,255))

        self.screen.blit(text_b, (self.sidebar_x + 20, 160))
        self.screen.blit(text_w, (self.sidebar_x + 20, 190))

        # PASS button
        pygame.draw.rect(self.screen, (0, 0, 0), self.pass_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pass_button, 2)

        btn_text = self.font.render("PASS", True, (255, 255, 255))
        self.screen.blit(
            btn_text,
            (self.pass_button.centerx - btn_text.get_width() // 2,
            self.pass_button.centery - btn_text.get_height() // 2)
        )
        if self.game.last_error:
            error_text = self.font.render(self.game.last_error, True, (255, 80, 80))
            self.screen.blit(error_text, (self.sidebar_x + 20, 120))
        
        if self.game.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game.game_over:
                        continue
                    x, y = pygame.mouse.get_pos()
                    # click to PASS
                    if self.pass_button.collidepoint(x, y):
                        self.game.pass_turn()
                        continue
                    # click the board
                    r, c = self.pixel_to_board(x, y)
                    self.game.play_move(r, c)

            if not self.game.game_over:

                if self.game.current_player == WHITE:  # AI是白
                    move = self.game.ai.select_move(self.game)

                    if move is None:
                        self.game.pass_turn()
                    else:
                        self.game.play_move(*move)
            self.draw()
            clock.tick(60)

    def draw_game_over(self):
        score = self.game.final_score

        # =========================
        # 1. 半透明遮罩
        # =========================
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # =========================
        # 2. 中心面板
        # =========================
        box_w, box_h = 300, 200
        box = pygame.Rect(
            WIDTH // 2 - box_w // 2,
            HEIGHT // 2 - box_h // 2,
            box_w,
            box_h
        )

        pygame.draw.rect(self.screen, (50, 50, 60), box, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), box, 2, border_radius=10)

        font = pygame.font.SysFont("Arial", 24)

        # =========================
        # 3. 内容
        # =========================
        black = font.render(f"Black: {score['black']:.1f}", True, (255,255,255))
        white = font.render(f"White: {score['white']:.1f}", True, (255,255,255))
        winner = font.render(f"Winner: {score['winner']}", True, (255,215,0))
        margin = font.render(f"Margin: {score['margin']:.1f}", True, (200,200,200))

        self.screen.blit(black, (box.x + 40, box.y + 30))
        self.screen.blit(white, (box.x + 40, box.y + 70))
        self.screen.blit(winner, (box.x + 40, box.y + 110))
        self.screen.blit(margin, (box.x + 40, box.y + 150))

if __name__ == "__main__":
    GoUI().run()