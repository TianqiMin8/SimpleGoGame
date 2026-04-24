# core_game.py
# TODO: Choose AI / Human can play first
# TODO: Allow human play all the move


from collections import deque
from ai import SmartAI

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
        self.ai = SmartAI(WHITE)
        self.last_move = None  # form: (row, col)
        self.last_state = None

    def _get_current_state(self):
        """Save current status into history"""
        state = {
            'grid': [row[:] for row in self.board.grid],
            'current_player': self.current_player,
            'last_move': self.last_move,
            'previous_board_grid': [row[:] for row in self.previous_board.grid] if self.previous_board else None,
            'captured': self.captured.copy(),
            'pass_count': self.pass_count,
            'game_over': self.game_over
        }
        return state

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
        
        if self.current_player == BLACK:
            self.last_state = self._get_current_state()
        
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
    

    def undo(self):
        if self.last_state is None:
            print("Cannot undo")
            return False
            
        state = self.last_state
        
        self.board.grid = state['grid']
        self.current_player = state['current_player']
        self.last_move = state['last_move']
        self.pass_count = state['pass_count']
        self.game_over = state['game_over']
        self.captured = state['captured']
        
        if state['previous_board_grid']:
            self.previous_board = Board(self.board.size)
            self.previous_board.grid = state['previous_board_grid']
        else:
            self.previous_board = None
            
        # only allow one undo 
        self.last_state = None
        return True