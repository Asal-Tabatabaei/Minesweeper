import pygame
import time
import random
from pyDatalog import pyDatalog
from src.minesweeper import MineSweeper

# =========================================================================
# Section 1: Define First-Order Logic Terms
# =========================================================================

AGENT_UNKNOWN = -1
AGENT_FLAGGED = -2

pyDatalog.clear()

pyDatalog.create_terms('X, Y, X2, Y2, N')
pyDatalog.create_terms('Neighbor, Revealed, FlaggedCount, TotalHiddenCount, IsUnknown')
pyDatalog.create_terms('Safe, Mine')

# ============================================================
# Static Facts & Rules
# ============================================================

def init_static_facts(rows, cols):
    Neighbor.clear()
    for r in range(rows):
        for c in range(cols):
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        + Neighbor(r, c, nr, nc)

def init_rules():
    Safe(X2, Y2) <= (
        Revealed(X, Y, N) & 
        FlaggedCount(X, Y, N) & 
        Neighbor(X, Y, X2, Y2) & 
        IsUnknown(X2, Y2)
    )

    Mine(X2, Y2) <= (
        Revealed(X, Y, N) & 
        TotalHiddenCount(X, Y, N) & 
        Neighbor(X, Y, X2, Y2) & 
        IsUnknown(X2, Y2)
    )

# ============================================================
# Knowledge Base Update
# ============================================================

def update_knowledge_base(agent_board, rows, cols):
    Revealed.clear()
    FlaggedCount.clear()
    TotalHiddenCount.clear()
    IsUnknown.clear()

    for r in range(rows):
        for c in range(cols):
            val = agent_board[(r, c)]
            
            if val == AGENT_UNKNOWN:
                + IsUnknown(r, c)
                
            elif val >= 0: 
                flagged_count = 0
                hidden_count = 0
                
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor_val = agent_board[(nr, nc)]
                            if neighbor_val == AGENT_FLAGGED:
                                flagged_count += 1
                                hidden_count += 1
                            elif neighbor_val == AGENT_UNKNOWN:
                                hidden_count += 1
                
                + Revealed(r, c, val)
                + FlaggedCount(r, c, flagged_count)
                + TotalHiddenCount(r, c, hidden_count)

# ============================================================
# Logical Solver Query
# ============================================================

def query_solver():
    safe_moves = []
    mine_moves = []
    
    safe_answers = Safe(X, Y)
    if safe_answers:
        safe_moves = list(set([ (ans[0], ans[1]) for ans in safe_answers.data ]))
        
    mine_answers = Mine(X, Y)
    if mine_answers:
        mine_moves = list(set([ (ans[0], ans[1]) for ans in mine_answers.data ]))
    
    return safe_moves, mine_moves


def get_safest_guess(agent_board, rows, cols):
    hidden = [pos for pos, val in agent_board.items() if val == AGENT_UNKNOWN]
    if not hidden:
        return None

    isolated = []
    for (r, c) in hidden:
        near_revealed = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if agent_board[(nr, nc)] >= 0:
                        near_revealed = True
                        break
            if near_revealed: break
        
        if not near_revealed:
            isolated.append((r, c))

    if isolated:
        return random.choice(isolated)
    return random.choice(hidden)

# ============================================================
# Main Agent Loop
# ============================================================

def prolog_solver(game):
    init_static_facts(game.rows, game.cols)
    init_rules()

    agent_board = {(r, c): AGENT_UNKNOWN for r in range(game.rows) for c in range(game.cols)}

    start_r, start_c = game.get_start_pos()
    value = game.reveal(start_r, start_c)
    agent_board[(start_r, start_c)] = value if value is not None else 0

    running = True
    while running and not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_knowledge_base(agent_board, game.rows, game.cols)

        safe_moves, mine_moves = query_solver()
        move_made = False

        for r, c in safe_moves:
            if agent_board[(r, c)] == AGENT_UNKNOWN:
                val = game.reveal(r, c)
                if val == -1:
                    agent_board[(r, c)] = AGENT_FLAGGED
                elif val is not None:
                    agent_board[(r, c)] = val
                move_made = True

        for r, c in mine_moves:
            if agent_board[(r, c)] == AGENT_UNKNOWN:
                game.flag(r, c)
                agent_board[(r, c)] = AGENT_FLAGGED
                move_made = True

        if not move_made and not game.game_over:
            guess = get_safest_guess(agent_board, game.rows, game.cols)
            if guess is None:
                break
            
            r, c = guess
            print(f"Deadlock! Applying smart heuristic at ({r}, {c})")
            val = game.reveal(r, c)
            if val == -1:
                agent_board[(r, c)] = AGENT_FLAGGED
            elif val is not None:
                agent_board[(r, c)] = val

        game.render()
        time.sleep(0.1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game.render()
    pygame.quit()

if __name__ == "__main__":
    ms = MineSweeper(rows=9, cols=9, mines=9, seed=99, auto_flood_fill=False)
    prolog_solver(ms)
