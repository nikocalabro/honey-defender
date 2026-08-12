import copy
from collections import deque
from traceback import format_list

import numpy as np

from . import constants
from .player_base import Player
from . import game_manager

"""
Board is the rules and state for a turn-based game.

- State: the grid of cell values (0 = empty, non-zero = a player's identifier)
- Rules: what moves are legal, how moves are applied, and how to detect win/tie

When changing this class to create new game you must:
- Define how a move is applied and verify the move is legal
- Update the game state after each move is applied
- Define how a winner, and or tie is determined

Note: All rendering should be done elsewhere. This class just contains the rules and state of the game

"""

class Board:
    #the 2 is for each side to call it, the left number is how many turns
    last_board_state = None
    turn_count = 0
    tie_counter = 0
    #if players are moving, but not pushing
    no_progress_counter = 0
    def __init__(self):
        self.rows = constants.NUM_ROWS
        self.cols = constants.NUM_COLS

        # 1 d list that has each hex in order, currently making an empty board
        self.game_board = [None] * self.rows * self.cols
        #this is the starting players identity
        identity = -1
        count_of_items = [0,None,0]
        for hex_num in range(self.rows * self.cols):
            if hex_num % self.rows == 0:
                identity = -identity
            count_of_items[identity+1] += 1
            self.game_board[hex_num] = identity
        Player.set_piece_count(count_of_items[0], -1)
        Player.set_piece_count(count_of_items[2], 1)

        self.last_player = None

        # last move as a tuple (row, col) on game_board
        self.winner = None

    #select_tile, target_tile , direction, self.current_player
    def apply_move(self, select_tile: int, target_tile: int, player) -> bool:

        """
        Calculates the direction of the push
        Calculates the push of the pieces, then updates the board with all of that information
        """

        # if they clicked within the hexes
        if target_tile is not None:
            #affected line is built by the indexes so it can change the board easier
            affected_line = [select_tile, target_tile]
            #build the affected line to push them
            direction = 0
            # 6 directions in a hexagon
            for i in range(6):
                # the difference between the selected tile and the target tile, if its matches one of the patterns
                # we want to store the dirrection
                if ((constants.HEX_LIST[target_tile][0] - constants.HEX_LIST[select_tile][0]) == constants.direction_patterns[i+1][0] and
                        (constants.HEX_LIST[target_tile][1] - constants.HEX_LIST[select_tile][1]) == constants.direction_patterns[i + 1][1]):
                    direction = i+1
                    break
            #reconvert into cords
            testing_tile = constants.HEX_LIST[target_tile]
            for i in range(self.rows * self.cols):
                #create a theoretical tile middle

                testing_tile = (testing_tile[0] + constants.direction_patterns[direction][0], testing_tile[1] + constants.direction_patterns[direction][1])

                # if the tile is a real tile add it to the list, ONLY IN ONE DIRECTION
                if testing_tile in constants.HEX_LIST:
                    # add the tile's index to the line thats being affected
                    affected_line.append(constants.HEX_LIST.index(testing_tile))
                else:
                    break
            # if the target spot has air
            if affected_line[1] == 0:
                self.no_progress_counter += 1
            else:
                self.no_progress_counter = 0
            # length -1 because the last piece is just gonna disappear

            i = 0
            copy = []
            for j in range(len(self.game_board)):
                copy.append(self.game_board[j])
            # pushes everything
            while i < len(affected_line)-1:
                if copy[affected_line[i]] == 0: #dont push air
                    break
                self.game_board[affected_line[i+1]] = copy[affected_line[i]]
                i += 1
            self.game_board[affected_line[0]] = 0 # this is where the player moved from
            #Counts to see if anything fell off
            # player 2, None, then player 1
            current_count_of_items = [0, None, 0]
            for hex_num in range(self.rows * self.cols):
                if self.game_board[hex_num] == 1:
                    current_count_of_items[0] += 1
                elif self.game_board[hex_num] == -1:
                    current_count_of_items[2] += 1
            # change the players piece count, if the new count is less
            REWARD = 10
            SUICIDE = 25
            # small constant
            if player.is_ai_player:
                player.feed_reward(-1)
            #PLAYER 2 death
            if current_count_of_items[0] < player.all_players[0].piece_count:
                if player == player.all_players[0] and player.is_ai_player:
                    # print("ursaring (p1) killed ursaring (p1)")
                    # NEGATIVE REWARDS FOR LETTING YOURSELF DIE
                    player.feed_reward(SUICIDE)
                    player.update_game_over_training_diagnostics("Suicides")
                else:
                    # print("beedrill (p2) killed ursaring (p1)")
                    # NEGATIVE REWARDS FOR LETTING YOURSELF DIE
                    if player.all_players[0].is_ai_player:
                        player.all_players[0].feed_reward(REWARD)
                    # POS REWARDS FOR KILLING OPPONENT
                    if player.all_players[1].is_ai_player:
                        # feed reward for killing opponent
                        # POINT for killing opponent
                        player.all_players[1].feed_reward(REWARD)
                        player.all_players[1].update_game_over_training_diagnostics("Killing Points")
                Player.change_piece_count(current_count_of_items[0] - player.all_players[0].piece_count, player.all_players[0].identifier)
            #PLAYER 1 death
            elif current_count_of_items[2] < player.all_players[1].piece_count:
                if player == player.all_players[1] and player.is_ai_player:
                    # print("beedrill (p2) killed beedrill (p2)")
                    # NEGATIVE REWARDS FOR LETTING YOURSELF DIE
                    player.feed_reward(SUICIDE)
                    player.update_game_over_training_diagnostics("Suicides")
                else:
                    # print("ursaring (p1) killed beedrill (p2)")
                    # NEGATIVE REWARDS FOR LETTING YOURSELF DIE
                    if player.all_players[1].is_ai_player:
                        player.all_players[1].feed_reward(REWARD)
                    if player.all_players[0].is_ai_player:
                        # feed reward for killing opponent
                        # POINT for killing opponent
                        player.all_players[0].feed_reward(REWARD)
                        player.all_players[0].update_game_over_training_diagnostics("Killing Points")


                Player.change_piece_count(current_count_of_items[2] - player.all_players[1].piece_count, player.all_players[1].identifier)
            return True
        return False
    def get_board_indicator(self,tile: int) -> int | None:
        return self.game_board[tile]

    def reset(self, starting_player_identity: int = -1):

        """
        Clear the game board and reset winner, and last_player for new game
        """
        self.tie_counter = 0
        self.game_board = np.zeros((self.rows, self.cols))
        self.winner = None
        self.last_player = None
        # 1 d list that has each hex in order, currently making an empty board
        self.game_board = [None] * self.rows * self.cols
        # this is the starting players identity
        identity = starting_player_identity
        count_of_items = [0, None, 0]
        for hex_num in range(self.rows * self.cols):
            if hex_num % self.rows == 0:
                identity = -identity
            count_of_items[identity + 1] += 1
            self.game_board[hex_num] = identity
        Player.set_piece_count(count_of_items[0], -1)
        Player.set_piece_count(count_of_items[2], 1)



    def check_winner(self, players: tuple) -> None:

        """
        Check whether the most recent move ended the game (win or tie).
        - Sets self.winner to the winning Player if the last move created a win.
        - Sets self.winner to "Tie" if the board is full and there is no winner.
        - Leaves self.winner as None if the game should continue. (No winner, or tie)
        """
        self.turn_count += 1
        # TO-QUESTION: For some reason the winners are switched
        if players[0].piece_count <= 1:
            self.winner = players[1]
        elif players[1].piece_count <= 1:
            self.winner = players[0]
        # CHECK TIE
        # if both players have gone, make the check for a tie
        if self.turn_count % 2 == 0:
            if self.game_board == self.last_board_state:
                self.tie_counter += 1
            else:
                self.tie_counter = 0
            self.last_board_state = copy.deepcopy(self.game_board)

        # Iif the board has been the same 3 times in a row (with each player getting a turn)
        # OR there has been no pushing for 30 moves
        if self.tie_counter >= 3 or self.no_progress_counter == 30:
            self.tie_counter = 0
            self.no_progress_counter = 0
            self.winner = "Tie"
            return



    def get_possible_moves(self, player) -> list[tuple[int, int]]:

        """
        Returns a list of all current players idetifier pieces indices
        """

        possible_moves = []
        for i in range(self.rows * self.cols):
                if self.game_board[i] == player.identifier:
                    possible_moves.append(i)
        return possible_moves




