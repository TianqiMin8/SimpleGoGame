# core_game.py

from collections import deque
from ai import RandomAI

EMPTY = 0
BLACK = 1
WHITE = 2


class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.final_score = None

    def get(self, r, c):
        if 0 <= r < self.size and 0 <= c < self.size:
            return self.grid[r][c]
        return None

    def set(self, r, c, color):
        self.grid[r][c] = color

    def copy(self):
        new_board = Board(self.size)
        new_board.grid = [row[:] for row in self.grid]
        return new_board



class Game:
    def __init__(self, size=9):
        self.board = Board(size)
        self.current_player = BLACK
        self.pass_count = 0
        self.game_over = False
        self.previous_board = None
        self.last_error = ""
        self.captured = {BLACK: 0, WHITE: 0}
        self.ai = RandomAI(WHITE)
        self.last_move = None  # form: (row, col)


    def _simulate_move(self, r, c, player):
        """
        return: (is_legal, captured_stones_list, error_msg)
        """
        if self.board.get(r, c) is None:
            return False, [], "Out of bounds"
        if self.board.get(r, c) != EMPTY:
            return False, [], "Position occupied"

        opponent = WHITE if player == BLACK else BLACK
        captured_stones = []
        
        # 1. temp move
        self.board.set(r, c, player)
        
        # 2. check neighbors are gwt or not
        for nr, nc in self.neighbors(r, c):
            if self.board.get(nr, nc) == opponent:
                group = self.get_group(nr, nc)
                if not self.has_liberty(group):
                    captured_stones.extend(list(group))
        
        # 3. Capture pieces and check for suicide moves.
        # If pieces were captured, the move is legal; 
        # if no pieces were captured, check if the moving group has any liberties remaining.
        is_suicide = False
        if not captured_stones:
            my_group = self.get_group(r, c)
            if not self.has_liberty(my_group):
                is_suicide = True
        
        # 4. KO check
        is_ko = False
        if not is_suicide:
            # temp remove captured stones, conpare with previous
            for pr, pc in captured_stones: self.board.set(pr, pc, EMPTY)
            
            if self.previous_board and self.board.grid == self.previous_board.grid:
                is_ko = True
                
            # move back
            for pr, pc in captured_stones: self.board.set(pr, pc, opponent)

        # 5. Roll back the temporary placement
        self.board.set(r, c, EMPTY)

        if is_suicide: return False, [], "Suicide move"
        if is_ko: return False, [], "KO violation"
        return True, captured_stones, ""

    def is_legal_move(self, r, c):
        legal, _, _ = self._simulate_move(r, c, self.current_player)
        return legal

    def get_legal_moves(self):
        """
        Get all legal places for stones.
        """
        moves = []
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.get(r, c) == EMPTY:
                    if self.is_legal_move(r, c):
                        moves.append((r, c))
        return moves

    def play_move(self, r, c):
        if self.game_over:
            return False
        
        legal, captured_stones, error = self._simulate_move(r, c, self.current_player)
        if not legal:
            self.last_error = error
            return False
        
        # stone placement logic
        # store current board to check KO
        old_board_obj = self.board.copy()
        
        # stone placement
        self.board.set(r, c, self.current_player)
        self.last_move = (r, c)

        # capture stones
        for pr, pc in captured_stones:
            self.board.set(pr, pc, EMPTY)
        
        # update data
        self.captured[self.current_player] += len(captured_stones)
        self.previous_board = old_board_obj
        self.pass_count = 0
        self.switch_player()
        return True

    def get_group(self, r, c):
        color = self.board.get(r, c)
        if color == EMPTY or color is None: return set()
        
        group = set()
        stack = [(r, c)]
        while stack:
            curr = stack.pop()
            if curr not in group:
                group.add(curr)
                for nr, nc in self.neighbors(*curr):
                    if self.board.get(nr, nc) == color:
                        stack.append((nr, nc))
        return group

    def has_liberty(self, group):
        for r, c in group:
            for nr, nc in self.neighbors(r, c):
                if self.board.get(nr, nc) == EMPTY:
                    return True
        return False

    def switch_player(self):
        self.current_player = BLACK if self.current_player == WHITE else WHITE

    def neighbors(self, r, c):
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.board.size and 0 <= nc < self.board.size:
                yield nr, nc

    def pass_turn(self):
        """
        Pass
        """
        if self.game_over:
            return

        print(f"Player {self.current_player} PASS")
        self.last_move = None
        self.pass_count += 1

        # end game if pass 2
        if self.pass_count >= 2:
            self.game_over = True
            self.final_score = self.get_score()
            print(f"Game Over. Final Score: {self.final_score}")
            return

        # switch players and empty the board
        self.previous_board = None 
        self.switch_player()

    def get_score(self):
        from scoring import compute_score
        return compute_score(self.board)
    # # =========================
    # # 基础工具
    # # =========================
    # def switch_player(self):
    #     self.current_player = BLACK if self.current_player == WHITE else WHITE

    # def neighbors(self, r, c):
    #     for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
    #         yield r+dr, c+dc

    # # =========================
    # # 气 & 提子
    # # =========================
    # def get_group(self, board, r, c):
    #     color = board.get(r, c)
    #     if color == EMPTY:
    #         return set()

    #     visited = set()
    #     stack = [(r, c)]
    #     group = set()

    #     while stack:
    #         x, y = stack.pop()
    #         if (x, y) in visited:
    #             continue
    #         visited.add((x, y))
    #         group.add((x, y))

    #         for nx, ny in self.neighbors(x, y):
    #             if board.get(nx, ny) == color:
    #                 stack.append((nx, ny))
    #     return group

    # def has_liberty(self, group):
    #     for r, c in group:
    #         for nr, nc in self.neighbors(r, c):
    #             if self.board.get(nr, nc) == EMPTY:
    #                 return True
    #     return False

    # def remove_group(self, group):
    #     color = self.board.get(*next(iter(group)))  # the color of stone that get captured

    #     for r, c in group:
    #         self.board.set(r, c, EMPTY)

    #     # Update the number of captured stones
    #     if color in (BLACK, WHITE):
    #         self.captured[self.current_player] += len(group)

    
    # def play_move(self, r, c):
    #     if self.game_over:
    #         print("Game over")
    #         return False
        
    #     self.last_error = ""
    #     if self.board.get(r, c) is None:
    #         self.last_error = "Out of bounds"
    #         return False

    #     if self.board.get(r, c) != EMPTY:
    #         self.last_error = "Position occupied"
    #         return False
        
    #     old_board = self.board.copy()

    #     # temporary move
    #     self.board.set(r, c, self.current_player)

    #     opponent = BLACK if self.current_player == WHITE else WHITE

    #     # capture check
    #     captured_any = False
    #     for nr, nc in self.neighbors(r, c):
    #         if self.board.get(nr, nc) == opponent:
    #             group = self.get_group(nr, nc)
    #             if not self.has_liberty(group):
    #                 self.remove_group(group)
    #                 captured_any = True

    #     # suicide move check
    #     my_group = self.get_group(r, c)
    #     if not self.has_liberty(my_group) and not captured_any:
    #         self.board.set(r, c, EMPTY)
    #         self.last_error = "Suicide move"
    #         return False
        
    #     # KO check
    #     if self.previous_board and self.board.grid == self.previous_board.grid:
    #         # move back
    #         self.board = old_board
    #         self.last_error = "KO violation"
    #         return False

        
    #     # successful move
    #     self.pass_count = 0
    #     self.switch_player()
    #     self.previous_board = old_board
    #     return True

    # # =========================
    # # PASS
    # # =========================
    # def pass_turn(self):
    #     if self.game_over:
    #         return

    #     print(f"Player {self.current_player} PASS")

    #     self.pass_count += 1

    #     if self.pass_count >= 2:
    #         self.game_over = True
    #         self.final_score = self.get_score()
    #         print("Game Over")
    #         return

    #     self.switch_player()

    # # =========================
    # # print the board (just for testing)
    # # =========================
    # def print_board(self):
    #     symbols = {EMPTY: ".", BLACK: "X", WHITE: "O"}
    #     for row in self.board.grid:
    #         print(" ".join(symbols[x] for x in row))
    #     print()

    # def get_score(self):
    #     from scoring import compute_score
    #     return compute_score(self.board)
    
    # def get_legal_moves(self):
    #     moves = []

    #     for r in range(self.board.size):
    #         for c in range(self.board.size):
    #             if self.board.get(r, c) == EMPTY:
    #                 # check move is legal
    #                 temp = self.board.get(r, c)
    #                 ok = self.is_legal_move(r, c)
    #                 if ok:
    #                     moves.append((r, c))

    #     return moves


    # def is_legal_move(self, r, c):
    #     if self.board.get(r, c) != EMPTY:
    #         return False

    #     temp_board = self.board.copy()

    #     # 临时落子
    #     temp_board.set(r, c, self.current_player)

    #     opponent = BLACK if self.current_player == WHITE else WHITE

    #     # 模拟提子
    #     captured_any = False
    #     for nr, nc in self.neighbors(r, c):
    #         if temp_board.get(nr, nc) == opponent:
    #             group = self.get_group(nr, nc)
    #             if not self.has_liberty(group):
    #                 captured_any = True

    #     # suicide check
    #     my_group = self.get_group(r, c)
    #     if not self.has_liberty(my_group) and not captured_any:
    #         return False

    #     return True
