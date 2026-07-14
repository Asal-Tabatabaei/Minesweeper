import pygame
import time
import random
from pyDatalog import pyDatalog
from src.minesweeper import MineSweeper

# =========================================================================
# Section 1: Define First-Order Logic Terms (FOL Terms)
# =========================================================================
pyDatalog.create_terms('R, C, R2, C2, N, Adj, Revealed, Flagged, Hidden, Safe, Mine, TempSafe, TempMine')
pyDatalog.create_terms('FlaggedNeighborCount, HiddenNeighborCount')

# Suggested constants for the agent's internal memory (Shadow Board)
AGENT_UNKNOWN = -1
AGENT_FLAGGED = -2

# =========================================================================
# Section 2: Generation of Logical Facts and Rules
# =========================================================================

def init_static_facts(rows, cols):
    """
    Task 1: Generate static facts at the beginning of the game 
    (adjacency relationships between cells).
    """
    pyDatalog.assert_fact('Adj', None, None, None, None)
    pyDatalog.load('') 
    
    for r in range(rows):
        for c in range(cols):
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        + Adj(r, c, nr, nc)

def init_rules():
    """
    Task 2: Define logical inference rules (Safety Rule and Danger Rule).
    """
    pyDatalog.load('')

    (FlaggedNeighborCount[R, C] == len(R2)) <= Adj(R, C, R2, C2) & Flagged(R2, C2)
    
    (HiddenNeighborCount[R, C] == len(R2)) <= Adj(R, C, R2, C2) & Hidden(R2, C2)

    
    TempMine(R2, C2) <= Revealed(R, C, N) & Adj(R, C, R2, C2) & Hidden(R2, C2) & (N == HiddenNeighborCount[R, C])
   
    TempSafe(R2, C2) <= Revealed(R, C, N) & Adj(R, C, R2, C2) & Hidden(R2, C2) & (N == FlaggedNeighborCount[R, C])

    Mine(R, C) <= TempMine(R, C)
    Safe(R, C) <= TempSafe(R, C)

def update_knowledge_base(agent_board, rows, cols):
    """
    Task 3: Convert the agent's internal memory (agent_board) into dynamic facts in each turn.
    Before adding new facts, facts from the previous turn must be cleared.
    """
    pyDatalog.assert_fact('Revealed', None, None, None)
    pyDatalog.assert_fact('Flagged', None, None)
    pyDatalog.assert_fact('Hidden', None, None)
    pyDatalog.assert_fact('TempSafe', None, None)
    pyDatalog.assert_fact('TempMine', None, None)
    
    for (r, c), val in agent_board.items():
        if val == AGENT_UNKNOWN:
            + Hidden(r, c)
        elif val == AGENT_FLAGGED:
            + Flagged(r, c)
        elif val >= 0:
            + Revealed(r, c, val)

def query_solver():
    """
    Task 4: Query the inference engine to find safe cells and mines.
    Output: Two lists containing the coordinates of safe cells and mine cells.
    """
    safe_moves = []
    mine_moves = []
    
    safe_results = pyDatalog.ask('Safe(R, C)')
    if safe_results:
        safe_moves = list(safe_results.answers)
        
    mine_results = pyDatalog.ask('Mine(R, C)')
    if mine_results:
        mine_moves = list(mine_results.answers)
        
    return safe_moves, mine_moves
# =========================================================================
# Section 3: Uncertainty Handling Strategy (Smart Guess) - Optional/Bonus
# =========================================================================

def get_safest_guess(agent_board, rows, cols):
    """
    Task 5 (Optional): Calculate the probability of cells being mines during a logical deadlock.
    """
    return None

# =========================================================================
# Section 4: Main Agent Loop
# =========================================================================

def prolog_solver(game):
    # Initialize static facts and rules
    init_static_facts(game.rows, game.cols)
    init_rules()
    
    # Create agent's internal memory (Shadow Board) - initially all cells are unknown
    agent_board = {}
    for r in range(game.rows):
        for c in range(game.cols):
            agent_board[(r, c)] = AGENT_UNKNOWN

    # Get starting position (Guaranteed to be 0 and safe according to the project documentation)
    start_r, start_c = game.get_start_pos()
    print(f"Starting at guaranteed safe position: {start_r}, {start_c}")
    
    # First move: Reveal the starting cell and record it in the agent's memory
    start_val = game.reveal(start_r, start_c)
    agent_board[(start_r, start_c)] = start_val if start_val is not None else 0
    
    running = True
    while running and not game.game_over:
        # Handle Pygame events to prevent the window from freezing/crashing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Update the knowledge base based on the latest state of the agent's memory
        update_knowledge_base(agent_board, game.rows, game.cols)

        # 2. Query the logic engine
        safe_moves, mine_moves = query_solver()
        move_made = False

        # 3. Apply the extracted logical actions to the game environment and update memory
        # Hint: Reveal safe cells first, then flag the mine cells.
        
        # 4. Deadlock management (if no deterministic logical move is found)
        if not move_made and not game.game_over:
            print("Logical deadlock! Attempting guess...")
            # First use the Heuristic, and if no data is available, make a completely random choice
            pass

        # Render the environment and add a short delay to observe the solving process
        game.render()
        time.sleep(0.2)

    # Keep the window open after the game ends
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game.render()

if __name__ == "__main__":
    # Default settings based on the first scenario (Simple level) in the evaluation table
    # Note: auto_flood_fill must be False to preserve the encapsulation of the agent's memory.
    ms = MineSweeper(rows=9, cols=9, mines=10, seed=99, auto_flood_fill=False)
    prolog_solver(ms) 