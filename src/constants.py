import math
from pathlib import Path
from .utilities import create_shape

# File paths (where AI policies are stored)
BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / 'policies'

# File name of policy used when in Human play AI mode
POLICY_FILE = "hard_player2.pkl"
IGNORE_DELAY = False
# ----------------------------------------------------------------------------------------------------------------------

# AI Training Constants

# How strong to update a states value when learning new information
#   Higher value (ex > 0.5)  - learns faster but can become unstable
#   Lower values (ex < 0.05) - learns more smoothly but will take longer to train
# Choose a value between 0.01 and 0.3 for state based Reinforcement Learning
#
# When you are making your new game in your team you will want to experiment with different values
LEARNING_RATE = 0.05

# Discount factor: how much the AI should care about future rewards compared to immediate rewards
# Closer to 0: Care more about immediate rewards.
# Closer to 1: Care more about future (long term rewards)
# For tic-tac-toe this means care more about making the best more each turn (closer to 0), or care more about winning (closer to 1)
# If too small the AI will not learn multistep strategies that take more than one turn to develop.
DECAY_GAMMA = 0.97

# The starting value for our exploration vs exploitation. For exploration the AI will choose a random valid move.
# For exploitation the AI will choose the move has a better change in eventually winning.
EXPLORATION_RATE = 1.0

# How much the exploration rate decreases each episode (games played). The new exploration rate is calculated by
# new_exploration = EXPLORATION_RATE * EXPLORATION_DECAY_RATE
# When training we should start by exploring a lot. Then over the duration of time explore less and less
EXPLORATION_DECAY_RATE = 0.99997

# The minimum probability the AI will choose to explore
MIN_EXPLORATION_RATE = 0.02
SECOND_AI_MIN_EXPLORATION_RATE = 0.1

# Total number of training episodes. Each episode is one game complete game.
EPISODES = 100000

# How often to print training diagnostics to the console
TRAINING_DIAGNOSTICS_INTERVAL = 5000

# ----------------------------------------------------------------------------------------------------------------------

# Graphics Constants
FRAME_RATE = 60
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_ORANGE = (252, 153, 5)
COLOR_DEEP_ORANGE = (237, 167, 62)
COLOR_BLUE_GREEN = (4,100,100)
COLOR_BROWN = (97, 73, 28)
COLOR_DARK_GREEN = (18, 117, 25)
COLOR_GOLD = (237, 226, 90)
COLOR_LIGHT_BLUE = (178, 221, 242)
COLOR_RED_BROWN = (77, 34, 13)

PLAYER_1_COLOR = COLOR_GOLD
PLAYER_2_COLOR = COLOR_LIGHT_BLUE

# Game Board
BOARD_CENTER_X = int(WINDOW_WIDTH / 2)
BOARD_CENTER_Y = int(WINDOW_HEIGHT / 2)
CELL_SIZE = 175

#have an odd number of columns/rows for a fair game, make the cols the odd number
NUM_ROWS = 3
NUM_COLS = 4

# Hexagon side length in pixels
HEXAGON_SIDE_LENGTH = CELL_SIZE/2
HEXAGON_SHAPE = create_shape(6,HEXAGON_SIDE_LENGTH)

APOTHEM = math.sqrt(3) / 4 * CELL_SIZE
DIST = 3 * CELL_SIZE / 4
FIRST_CELL_CENTER = (BOARD_CENTER_X - (DIST * ((NUM_COLS - 1) / 2)),BOARD_CENTER_Y - (APOTHEM * (2 * NUM_ROWS - 1) / 2))
# Creates a list of every single Hexagon, which is constant after all of these constants have been selected
HEX_LIST = []
make_tile = [FIRST_CELL_CENTER[0], FIRST_CELL_CENTER[1]]
for c in range(NUM_COLS):
    for r in range(NUM_ROWS):
        #has to be separated otherwise it just makes all the values the same as the final tile
        HEX_LIST.append((make_tile[0],make_tile[1]))
        make_tile[1] += 2 * APOTHEM
    # this creates the starting position for the top hexagon, then shifts it up or down based of its col num
    make_tile[1] = FIRST_CELL_CENTER[1]
    if c % 2 == 0:
        make_tile[1] += APOTHEM
    make_tile[0] += DIST  # moves over to the right by one hexagon

BOARD_WIDTH = NUM_COLS * DIST
if NUM_ROWS % 2 == 0: BOARD_WIDTH -= DIST + CELL_SIZE
BOARD_HEIGHT = (2 * NUM_COLS + 1) * APOTHEM

# arrow Polygon
arrow_w = CELL_SIZE / 4
ARROW_SHAPE = [
    (-arrow_w // 2, -arrow_w // 4),
    (arrow_w // 6, -arrow_w // 4),
    (arrow_w // 6, -arrow_w // 2),
    (arrow_w // 2, 0),
    (arrow_w // 6, arrow_w // 2),
    (arrow_w // 6, arrow_w // 4),
    (-arrow_w // 2, arrow_w // 4)
]
# directions for each shift needed to find center around a certain point, (0,0) is just there to not get a key error
# the last value in the tuple is the rotation needed for an object to face the dirrection it pushed, assuming it was facing right before
direction_patterns = {
            0 : (0,0,0),
            1 : (0,-2*APOTHEM,-90),
            2 : (DIST,-APOTHEM,-30),
            3 : (DIST, APOTHEM,30),
            4 : (0,2*APOTHEM,90),
            5 : (-DIST,APOTHEM,150),
            6 : (-DIST,-APOTHEM,-150),
        }