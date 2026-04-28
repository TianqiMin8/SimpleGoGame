import pygame
import sys
from core_game import Game, BLACK, WHITE, EMPTY

BOARD_SIZE = 9
CELL_SIZE = 60
MARGIN = 40

BG_COLOR = (220, 179, 92)
COVER_COLOR = (48, 48, 48)
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


        self.state = "MENU"  
        self.mode = "PVE"    
        self.first_player = BLACK 

        self.game = None 
        self.sidebar_x = (BOARD_SIZE - 1) * CELL_SIZE + MARGIN * 2
        
        # Menu button
        btn_w, btn_h = 160, 40  
        spacing = 20            
        center_x = WIDTH // 2
        self.pvp_btn = pygame.Rect(center_x - btn_w - spacing//2, 180, btn_w, btn_h)

        self.pve_btn = pygame.Rect(center_x + spacing//2, 180, btn_w, btn_h)

        self.black_first_btn = pygame.Rect(center_x - btn_w - spacing//2, 280, btn_w, btn_h)
        self.white_first_btn = pygame.Rect(center_x + spacing//2, 280, btn_w, btn_h)

        self.start_btn = pygame.Rect(center_x - 100, 400, 200, 60)

        
        self.undo_button = pygame.Rect(self.sidebar_x + 40, HEIGHT - 130, 120, 40)
        self.pass_button = pygame.Rect(self.sidebar_x + 40, HEIGHT - 70, 120, 40)
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)

        # Set reset button position
        self.reset_button = pygame.Rect(self.sidebar_x + 40, HEIGHT - 190, 120, 40)

        # Set return button position
        self.return_button = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 150, 120, 40)


    def board_to_pixel(self, r, c):
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        return x, y

    def pixel_to_board(self, x, y):
        c = round((x - MARGIN) / CELL_SIZE)
        r = round((y - MARGIN) / CELL_SIZE)
        return r, c

    def draw_menu(self):
        self.screen.fill(COVER_COLOR)
        title = self.title_font.render("Wang's Go Game", True, WHITE_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        self._draw_option_btn(self.pvp_btn, "Human vs Human", self.mode == "PVP")
        self._draw_option_btn(self.pve_btn, "Human vs AI", self.mode == "PVE")

        self._draw_option_btn(self.black_first_btn, "Human first", self.first_player == BLACK)
        self._draw_option_btn(self.white_first_btn, "AI first", self.first_player == WHITE)

        pygame.draw.rect(self.screen, (0, 150, 0), self.start_btn, border_radius=10)
        start_txt = self.font.render("START GAME", True, (255, 255, 255))
        self.screen.blit(start_txt, start_txt.get_rect(center=self.start_btn.center))

    def _draw_option_btn(self, rect, text, is_selected):
        color = (206, 158, 67) if is_selected else (200, 200, 200)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2, border_radius=5)
        txt = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill(BG_COLOR)

        # draw lines and labels
        label_font = pygame.font.SysFont("Arial", 14)
        letters = "ABCDEFGHI" 

        for i in range(BOARD_SIZE):
            letter_text = label_font.render(letters[i], True, (50, 50, 50))
            x, y = self.board_to_pixel(0, i) 
            self.screen.blit(letter_text, (x - letter_text.get_width() // 2, MARGIN - 25))
            bottom_y = MARGIN + (BOARD_SIZE - 1) * CELL_SIZE
            self.screen.blit(letter_text, (x - letter_text.get_width() // 2, bottom_y + 10))
            number_text = label_font.render(str(BOARD_SIZE - i), True, (50, 50, 50))
            x, y = self.board_to_pixel(i, 0) 
            self.screen.blit(number_text, (MARGIN - 30, y - number_text.get_height() // 2))
            right_x = MARGIN + (BOARD_SIZE - 1) * CELL_SIZE
            self.screen.blit(number_text, (right_x + 15, y - number_text.get_height() // 2))

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
        
        self.draw_liberties()

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
        
        # Draw captured count
        text_x = self.sidebar_x + 20
        b = self.game.captured[BLACK]
        w = self.game.captured[WHITE]

        text_b = self.font.render(f"Black captured: {b}", True, (255,255,255))
        text_w = self.font.render(f"White captured: {w}", True, (255,255,255))

        self.screen.blit(text_b, (text_x + 20, 160))
        self.screen.blit(text_w, (text_x + 20, 190))

        # Draw current score
        scores = self.game.get_score()
        black_score = scores['black']
        white_score = scores['white']
        score_y = 90 

        b_text = self.font.render(f"Black: {black_score}", True, (255, 255, 255))
        w_text = self.font.render(f"White: {white_score}", True, (255, 255, 255))
        self.screen.blit(b_text, (text_x + 20, score_y))
        self.screen.blit(w_text, (text_x + 20, score_y + 30))


        # Reset button
        pygame.draw.rect(self.screen, (150, 50, 50), self.reset_button, border_radius=5)
        reset_txt = self.font.render("RESET", True, (255, 255, 255))
        self.screen.blit(reset_txt, reset_txt.get_rect(center=self.reset_button.center))

        # Undo button 
        # current_undo_color = self.undo_btn_color if self.game.last_state else (150, 150, 150)
        pygame.draw.rect(self.screen, (0, 0, 0), self.undo_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.undo_button, 2)
        undo_text = self.font.render("Undo", True, (255, 255, 255))
        self.screen.blit(
            undo_text,
            (self.undo_button.centerx - undo_text.get_width() // 2,
            self.undo_button.centery - undo_text.get_height() // 2)
        )

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
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    if self.state == "MENU":
                        if self.pvp_btn.collidepoint(x, y): self.mode = "PVP"
                        if self.pve_btn.collidepoint(x, y): self.mode = "PVE"
                        if self.black_first_btn.collidepoint(x, y): self.first_player = BLACK
                        if self.white_first_btn.collidepoint(x, y): self.first_player = WHITE
                        
                        if self.start_btn.collidepoint(x, y):
                            self.game = Game(BOARD_SIZE)
                            self.game.current_player = BLACK                             
                            self.user_color = self.first_player                            
                            self.state = "PLAYING"

                    elif self.state == "PLAYING":
                        if self.game.game_over:
                            if self.return_button.collidepoint(x, y):
                                self.state = "MENU" 
                                continue
                        if self.reset_button.collidepoint(x, y):
                            self.game = Game(BOARD_SIZE) 
                            self.game.current_player = BLACK
                            continue

                        if self.pass_button.collidepoint(x, y):
                            self.game.pass_turn()
                        elif self.undo_button.collidepoint(x, y):
                            self.game.undo()
                        else:
                            r, c = self.pixel_to_board(x, y)
                            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                                self.game.play_move(r, c)

                if event.type == pygame.KEYDOWN and self.state == "PLAYING":
                    if event.key == pygame.K_u:
                        self.game.undo()

            if self.state == "PLAYING" and not self.game.game_over:
                if self.mode == "PVE":
                    if self.game.current_player != self.user_color:
                        move = self.game.ai.select_move(self.game)
                        if move is None:
                            self.game.pass_turn()
                        else:
                            self.game.play_move(*move)

            if self.state == "MENU":
                self.draw_menu()
            else:
                self.draw()

            pygame.display.flip()
            clock.tick(60)

    def draw_game_over(self):
        score = self.game.final_score
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

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

        black = font.render(f"Black: {score['black']:.1f}", True, (255,255,255))
        white = font.render(f"White: {score['white']:.1f}", True, (255,255,255))
        winner = font.render(f"Winner: {score['winner']}", True, (255,215,0))
        margin = font.render(f"Margin: {score['margin']:.1f}", True, (200,200,200))

        self.screen.blit(black, (box.x + 40, box.y + 30))
        self.screen.blit(white, (box.x + 40, box.y + 70))
        self.screen.blit(winner, (box.x + 40, box.y + 110))
        self.screen.blit(margin, (box.x + 40, box.y + 150))

        pygame.draw.rect(self.screen, (100, 100, 100), self.return_button, border_radius=5)
        ret_txt = self.font.render("RETURN", True, (255, 255, 255))
        self.screen.blit(ret_txt, ret_txt.get_rect(center=self.return_button.center))

    # only show liberty for the current player
    def draw_liberties(self):
        liberty_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        current_player = self.game.current_player
        
        color = (0, 0, 0, 80) if current_player == BLACK else (255, 255, 255, 120)
        radius = 6
        drawn_pos = set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.game.board.get(r, c) == current_player:
                    for nr, nc in self.game.board.get_neighbors(r, c):
                        if self.game.board.get(nr, nc) == EMPTY:
                            if (nr, nc) not in drawn_pos:
                                pos = self.board_to_pixel(nr, nc)
                                pygame.draw.circle(liberty_surface, color, pos, radius)
                                drawn_pos.add((nr, nc))

        self.screen.blit(liberty_surface, (0, 0))

    # Another way to draw liberties,     
    # Draw both side's liberties, point shared liberties to red
    # def draw_liberties(self):
    #     liberty_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    #     BLACK_COLOR = (0, 0, 0, 80)        
    #     WHITE_COLOR = (255, 255, 255, 120)  
    #     SHARED_COLOR = (255, 50, 50, 150)  
    #     radius = 6
    #     liberty_map = {}
    #     for r in range(BOARD_SIZE):
    #         for c in range(BOARD_SIZE):
    #             stone = self.game.board.get(r, c)
    #             if stone == EMPTY: continue
    #             for nr, nc in self.game.board.get_neighbors(r, c):
    #                 if self.game.board.get(nr, nc) == EMPTY:
    #                     if (nr, nc) not in liberty_map:
    #                         liberty_map[(nr, nc)] = set()
    #                     liberty_map[(nr, nc)].add(stone)
    #     for (r, c), owners in liberty_map.items():
    #         pos = self.board_to_pixel(r, c)
    #         if len(owners) > 1:
    #             # a shared liberty
    #             pygame.draw.circle(liberty_surface, SHARED_COLOR, pos, radius + 2) # 稍微大一点
    #         else:
    #             owner = list(owners)[0]
    #             color = BLACK_COLOR if owner == BLACK else WHITE_COLOR
    #             pygame.draw.circle(liberty_surface, color, pos, radius)
    #     self.screen.blit(liberty_surface, (0, 0))

if __name__ == "__main__":
    GoUI().run()