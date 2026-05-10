import asyncio
import json
import logging
import os
import sys
import numpy as np
import math

from base_agent import BaseC4Agent
from websockets.asyncio.client import connect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROWS = 6
COLS = 7


def get_valid_columns(board):
    return [col for col in range(len(board[0])) if board[0][col] == 0]

def drop_piece(board, col, piece):
    for row in range(len(board)-1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = piece
            return
        
def check_win(board, piece):
    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != piece:
                continue
            for dr, dc in directions:
                count = 1
                # Check in positive direction
                for i in range(1, 4):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == piece:
                        count += 1
                    else:
                        break
                # Check in negative direction
                for i in range(1, 4):
                    nr, nc = r - dr * i, c - dc * i
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == piece:
                        count += 1
                    else:
                        break
                if count >= 4:
                    return piece
    return 0


def is_terminal(board, my_piece, opponent_piece):
    return (
        check_win(board, my_piece) or
        check_win(board, opponent_piece) or
        len(get_valid_columns(board)) == 0
    )

def evaluate_window(window, piece, opponent_piece):
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4 
    elif window.count(opponent_piece) == 2 and window.count(0) == 2:
        score -= 1

    return score    

def score_position(board, piece, opponent_piece):
    score = 0

    column_weights = [0, 1, 3, 5, 3, 1, 0] 
    for col in range(COLS):
        col_array = [int(i) for i in list(board[:, col])]
        score += col_array.count(piece) * column_weights[col]

    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece, opponent_piece)

    for c in range(COLS):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece, opponent_piece)

    for r in range(3,ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece, opponent_piece)

    for r in range(3,ROWS):
        for c in range(3,COLS):
            window = [board[r-i][c-i] for i in range(4)]
            score += evaluate_window(window, piece, opponent_piece)

    return score

def minimax(board, depth, maximizing_player, my_piece, opponent_piece):
    if depth == 0 or is_terminal(board, my_piece, opponent_piece):
        if check_win(board, my_piece):
            return None, math.inf
        elif check_win(board, opponent_piece):
            return None, -math.inf
        elif len(get_valid_columns(board)) == 0:
            return None, 0
        else:
            return None, score_position(board, my_piece, opponent_piece)

    best_col = None
    if maximizing_player:
        best_score = -np.inf
        for col in get_valid_columns(board):
            b = board.copy()
            drop_piece(b, col, my_piece)
            _, score = minimax(b, depth-1, False, my_piece, opponent_piece)
            if score > best_score:
                best_score, best_col = score, col
        return best_col, best_score
    else:
        best_score = np.inf
        for col in get_valid_columns(board):
            b = board.copy()
            drop_piece(b, col, opponent_piece)
            _, score = minimax(b, depth-1, True, my_piece, opponent_piece)
            if score < best_score:
                best_score, best_col = score, col
        return best_col, best_score

class MinimaxAgent(BaseC4Agent):
    def __init__(self, server_uri=None):
        super().__init__(server_uri)
        self.board = None
        self.my_piece = None
        self.opponent_piece = None

    async def run(self) -> None:
        try:
            async with connect(self.server_uri) as websocket:
                await websocket.send(json.dumps({"client": "agent"}))

                async for message in websocket:
                    if isinstance(message, bytes):
                        message = message.decode("utf-8")
                    data = json.loads(message)

                    if data.get("type") == "setup":
                        self.player_id = data.get("player_id")
                        self.my_piece = self.player_id
                        self.opponent_piece = 3 - self.player_id
                        logging.info(f"Connected! Assigned Player {self.player_id}")

                    elif data.get("type") == "state":
                        self.board = np.array(data.get("board"))
                        current_turn = data.get("current_turn")
                        valid_actions = data.get("valid_actions")

                        if current_turn == self.player_id and isinstance(valid_actions, list):
                            action = await self.deliberate(valid_actions)
                            if action is not None:
                                await websocket.send(json.dumps({"action": "move", "column": action}))

                    elif data.get("type") == "game_over":
                        logging.info(f"Round Over: {data.get('message')}")
                        logging.info("Waiting for next round to start...")

        except Exception as e:
            logging.error(f"Connection lost: {e}")

    async def deliberate(self, valid_actions):
        col, score = await asyncio.to_thread(minimax, self.board, 4, True, self.my_piece, self.opponent_piece)
        logging.info(f"Minimax selected column {col} with score {score}")
        return col if col in valid_actions else None
    
if __name__ == "__main__":
    agent = MinimaxAgent()
    asyncio.run(agent.run())