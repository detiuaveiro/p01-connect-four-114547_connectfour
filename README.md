[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ovfM0qtv)
# <img src="frontend/favicon.svg" alt="logo" width="128" height="128" align="middle"> SI2 - Connect Four

Connect Four is a classic two-player connection board game in which the players choose a color and then take turns dropping colored discs into a seven-column, six-row vertically suspended grid. The pieces fall straight down, occupying the lowest available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs.

In this project, we focus on developing autonomous agents that can play Connect Four against each other or against a human player. The game state is managed by a central server that communicates with the agents and a frontend viewer via WebSockets. Each agent receives the current board state and must decide the best column to drop their disc.

## Game Rules

The game is played on a grid with $R=6$ rows and $C=7$ columns. Two players, Player 1 and Player 2, take turns dropping their pieces.
- **State**: The world state is represented by a 2D grid of size $6 \times 7$, where 0 represents an empty cell, 1 represents a disc from Player 1, and 2 represents a disc from Player 2.
- **Actions**: A player can choose a column index $c \in \{0, 1, \dots, 6\}$ that is not yet full (i.e., the top row of that column is 0).
- **Gravity**: When a player chooses a column, the piece falls to the lowest available row $r$ in that column.
- **Win Condition**: A player wins if they have 4 of their discs in a row (horizontal, vertical, or diagonal).
- **Draw**: The game ends in a draw if the board is full and no player has won.

## Setup

The "simulation" is launched using Docker Compose, which starts the backend server and the frontend viewer.

1.  **Start the environment**:
    ```bash
    docker compose up
    ```
    The frontend viewer will be available at `http://localhost:8080`.

2.  **Run Agents**:
    Create a virtual environment and install the dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    Execute the agents locally:
    ```bash
    python agents/dummy_agent.py
    ```
    or
    ```bash
    python agents/manual_agent.py
    ```

## Project Structure

- `backend/`: contains the server-side Python code (`server.py`) and its `Dockerfile`. The server manages the game state, scores, and communication.
- `frontend/`: contains the viewer (HTML, JS, CSS) to monitor the game state.
- `agents/`: contains the Connect Four agents:
    - `base_agent.py`: the abstract base class for agents.
    - `dummy_agent.py`: a simple automated agent that makes random moves.
    - `manual_agent.py`: an agent that allows manual player interaction via the terminal.
- `compose.yml`: Docker Compose configuration to run the backend and frontend.

## Development

To develop a new agent, you should inherit from the `BaseC4Agent` class and implement the `deliberate` method.

```python
from agents.base_agent import BaseC4Agent
import random

class MyAgent(BaseC4Agent):
    async def deliberate(self, valid_actions):
        # Your logic here
        return random.choice(valid_actions)
```

For more details on the API, please refer to the [documentation](https://mariolpantunes.github.io/si2-connect-four/).

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
