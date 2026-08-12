import math

from . import constants
from .player_base import Player
from .utilities import bounding_polygon


"""
human_player.py

HumanPlayer converts mouse input (x, y pixel coordinates) into a board move (row, col).

This class does NOT apply the move to the board. It only returns the move.
The GameManager is responsible for validating and applying the move.
"""

# selectingTile = True

class HumanPlayer(Player):

    def __init__(self, is_player_one):
        super().__init__(is_player_one)
        self.is_ai_player = False
        self.selectingTile = True
        self.select_tile = None
        self.target_tile = None
        self.affected_line = []
        self.direction = 1



    def choose_move(self, board, move_input) -> tuple|None:

        """
        Convert move_input (mouse click in pixels) into a board move (indices).

        Notes:
        - choose_move overrides the base class method.
        - This method uses the constant hex list, which stores the centers of each hex, to figure out if its in a hex.
        - This method does not apply moved directly to the board.
        - This method must be valid, it will not return an indices if its not a valid hex.
        - This method does not

        Returns None if the click is outside the board.
        """
        global selectingTile

        if move_input is None:
            return None
        # 1ST CLICK
        if self.selectingTile:
            count = 0
            # hex center represents the tuple that is the center of the hex
            # if rectangle_bounding_box(constants.BOARD_WIDTH, constants.BOARD_HEIGHT, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y), move_input):
            for hex_center in constants.HEX_LIST:
                if bounding_polygon(6, constants.HEXAGON_SIDE_LENGTH, hex_center, move_input) and board.get_board_indicator(count) == self.identifier:
                    # this is the tile that the player selected
                    self.select_tile = count
                    # move onto the next stage
                    self.selectingTile = False
                count += 1
        # 2ND CLICK
        else:
            #code to get the second tile
            count = 0
            # hex center represents the tuple that is the center of the hex
            for hex_center in constants.HEX_LIST:
                if bounding_polygon(6, constants.HEXAGON_SIDE_LENGTH, hex_center, move_input):
                    # this is the tile that the player selected, but its the target because its where they are trying to go
                    self.target_tile = count
                count += 1
            if self.target_tile is None:
                return None
            # this means that the 2nd tile selected (target tile) is adjacent to the first tile (select_tile) selected
            if self.find_adjacent(self.select_tile) is not None and self.target_tile in self.find_adjacent(self.select_tile):
                # these are adjacent to eachother
                self.selectingTile = True
                return self.select_tile,self.target_tile
            else:
                # go back to selecting a tile
                self.selectingTile = True
                self.select_tile = None
                self.target_tile = None

        return None








