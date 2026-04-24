# TODO: Why I use

import copy
import random

class RandomAI:
    def __init__(self, color):
        self.color = color

    def select_move(self, game):
        moves = game.get_legal_moves()
        # print("legal moves:", len(moves))
        
        if not moves:
            return None  # pass

        return random.choice(moves)
    


class SmartAI:
    def __init__(self, color):
        self.color = color

    def select_move(self, game):
        legal_moves = game.get_legal_moves()
        if not legal_moves: return None

        best_score = -999
        best_move = random.choice(legal_moves)

        for move in legal_moves:
            score = self.evaluate_move(game, move)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def evaluate_move(self, game, move):
        r, c = move
        score = 0
        
        # 1. 基础分：占据中心位置 (9x9 棋盘的 4,4 是中心)
        dist_to_center = abs(r - 4) + abs(c - 4)
        score += (8 - dist_to_center) * 0.5 

        # 2. 模拟落子看收益
        # 注意：这里只模拟一步，不跑完整个游戏，所以极快
        original_grid = [row[:] for row in game.board.grid]
        captured_count = self.get_capture_count(game, move)
        score += captured_count * 10  # 提子奖励极高

        return score

    def get_capture_count(self, game, move):
        # 简化版逻辑：只看这一步能提掉对方多少子
        # 我们可以复用你 play_move 里的逻辑，但只运行一次
        legal, captured, _ = game._simulate_move(move[0], move[1], self.color)
        return len(captured) if legal else -100