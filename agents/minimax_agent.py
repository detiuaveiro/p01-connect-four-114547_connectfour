from agents.base_agent import BaseC4Agent

def get_valid_columns(board):
    return [col for col in range(len(board[0])) if board[0][col] == 0]

def drop_piece(board, col, piece):
    for row in range(len(board)-1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = piece
            return
        
def check_win(board, piece):
    #TODO
    pass

def is_terminal(board, my_piece, opponent_piece):
    return (
        check_win(board, my_piece) or
        check_win(board, opponent_piece) or
        len(get_valid_columns(board)) == 0
    )

def minimax(board, depth, maximizing_player, my_piece, opponent_piece):
    #TODO
    pass

class MinimaxAgent(BaseC4Agent):
    async def deliberate(self, valid_actions):
        # TODO: Implement the deliberate method
        pass