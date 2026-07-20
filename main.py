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
