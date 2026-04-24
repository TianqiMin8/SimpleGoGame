from collections import deque
from core_game import EMPTY, BLACK, WHITE


def compute_score(board, komi=2.5):
    size = board.size
    visited = set()

    black_territory = 0
    white_territory = 0

    # 1. Compute territory
    for r in range(size):
        for c in range(size):

            if board.get(r, c) != EMPTY or (r, c) in visited:
                continue

            queue = deque([(r, c)])
            region = set()
            borders = set()

            while queue:
                x, y = queue.popleft()

                if (x, y) in visited:
                    continue

                visited.add((x, y))
                region.add((x, y))

                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    val = board.get(nx, ny)

                    if val == EMPTY:
                        queue.append((nx, ny))
                    elif val is not None:
                        borders.add(val)

            if len(borders) == 1:
                owner = list(borders)[0]
                if owner == BLACK:
                    black_territory += len(region)
                elif owner == WHITE:
                    white_territory += len(region)

    # 2. Compute stones
    black_stones = sum(row.count(BLACK) for row in board.grid)
    white_stones = sum(row.count(WHITE) for row in board.grid)

    # 3. Total score
    black_score = black_stones + black_territory
    white_score = white_stones + white_territory + komi

    return {
        "black": black_score,
        "white": white_score,
        "winner": "Black" if black_score > white_score else "White",
        "margin": abs(black_score - white_score)
    }