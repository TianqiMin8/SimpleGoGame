from core_game import Game

g = Game(5)

g.play_move(2, 2)
g.play_move(2, 3)
g.play_move(3, 2)
g.play_move(3, 3)

g.print_board()

g.pass_turn()
g.pass_turn()