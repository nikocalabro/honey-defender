
"""
player_base.py

Base class for AI and human players.
"""
from src import constants


class Player:
    all_players = []
    def __init__(self, is_player_one: bool):
        self.is_player_one = is_player_one
        self.piece_count = 0
        # These identifiers are used by Board to store moves in a numpy grid. DO NOT change from 1 and -1, these are used in the board init
        self.identifier = None
        if is_player_one:
            self.identifier = 1
        else:
            self.identifier = -1

        # Intended to be set by derived classes (HumanPlayer / AIPlayer)
        self.is_ai_player = None
        Player.all_players.append(self)


    def choose_move(self, board, move_input):

        """
        Choose a move to apply to the board.
        This method must be implemented by subclasses.
        """

        raise NotImplementedError("Derived classes must implement choose_move().")
    def get_identifier(self):
        return self.identifier
    @classmethod
    def set_piece_count(cls,new_count:int, identity:int):
        try:
            if cls.all_players[0].identifier == identity:
                cls.all_players[0].piece_count = new_count
            else:
                cls.all_players[1].piece_count = new_count
        except IndexError:
            pass

    @classmethod
    #identity is the identity of the pieces count being changed
    def change_piece_count(cls, adding: int, identity: int):
        #if we are taking away a piece, and its the other players piece reward them
        try:
            if cls.all_players[0].identifier == identity:
                cls.all_players[0].piece_count += adding
            elif cls.all_players[1].identifier == identity:
                cls.all_players[1].piece_count += adding
            else:
                print("Wrong Identity Entered!")
        except IndexError:
            pass
    @classmethod
    def find_adjacent(cls,tile: int) -> list | None:
        if tile is None:
            return None
        ret = []

        row = tile % constants.NUM_ROWS
        col = tile // constants.NUM_ROWS

        # same col:
        if row > 0:
            ret.append(tile - 1)
        if row < constants.NUM_ROWS - 1:
            ret.append(tile + 1)

        # diff col:
        if col < constants.NUM_COLS - 1:
            ret.append(tile + constants.NUM_ROWS)
            if col % 2 == 0 and row > 0:
                ret.append(tile + constants.NUM_ROWS - 1)
            elif (col + 1) % 2 == 0 and row < constants.NUM_ROWS - 1:
                ret.append(tile + constants.NUM_ROWS + 1)
        if col > 0:
            ret.append(tile - constants.NUM_ROWS)
            if col % 2 == 0 and row > 0:
                ret.append(tile - constants.NUM_ROWS - 1)
            elif (col + 1) % 2 == 0 and row < constants.NUM_ROWS - 1:
                ret.append(tile - constants.NUM_ROWS + 1)

        return ret

