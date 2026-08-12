from . import constants
from .board import Board
from enum import Enum

from .player_base import Player

"""
game_manager.py

GameManager runs the turn-based game loop logic (NOT the pygame loop).

Responsibilities:
- Owns the Board and the two Player objects
- Tracks whose turn it is
- Asks the current player to choose a move
- Applies the move to the board (using board.apply_move)
- Checks for a winner/tie after each valid move
- Switches turns when the game continues
- During AI training: records AI states and feeds rewards when the game ends

Important:
- GameManager contains no rendering or pygame code.
- Player objects only CHOOSE moves. GameManager applies moves and advances the game.
"""



class GameState(Enum):
    # START = -1
    PLAYING = 0     # game is active, moves are still being applied
    GAME_OVER = 1   # a player has won the game, or game ended in a tie
    RESET = 2       # waiting to reset (waiting to start a new game)


class GameManager:
    starting_player1 = True
    def __init__(self, player1, player2):
        self.board = Board()

        # players can either be Human or AI players
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.player1

        self.game_state = GameState.PLAYING
        # self.game_state = GameState.START

    def update(self, pending_move):

        """
        Advance the game by at most ONE move.

        pending_move: Human player only - (x, y) mouse click pixels

        Each move follows the following rules:
        1. Ask the current player to choose a move
        2. Apply the chosen move to the board
        3. If move was valid:
            - If current player is AI player record the move state
            - Check for game over (winner or tie)
            - If game over:
                - AI players feed reward
                - restart game
            - If not game over then set current player to other player

        """


        if self.game_state != GameState.PLAYING:
            return
        tiles = self.current_player.choose_move(self.board, pending_move)
        if tiles is None:
            return
        select_tile = tiles[0]
        target_tile = tiles[1]
        # apply the move
        if self.board.apply_move(select_tile, target_tile, self.current_player):

            #This code doesn't need changing
            if self.current_player.is_ai_player:
                self.current_player.add_state(self.board)

            self.board.check_winner((self.player1,self.player2))
            if self.board.winner is not None:
                self.feed_rewards(self.board.winner)
                self.game_state = GameState.GAME_OVER
            else:
                self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def feed_rewards(self, winning_player):

        """
        Give end-of-game rewards to AI players.

        - Tie: no rewards given
        - Winning AI: reward = 1
        - Losing AI: reward = 0
        """
        if winning_player == "Tie":
            if self.player1.is_ai_player:
                self.player1.feed_reward(25  + self.player1.kill_bonus)
                self.player1.update_game_over_training_diagnostics("ties")
            if self.player2.is_ai_player:
                self.player2.feed_reward(25 + self.player2.kill_bonus)
                self.player2.update_game_over_training_diagnostics("ties")
            return
        if winning_player == self.player1:
            loosing_player = self.player2
            if winning_player.is_ai_player:
                winning_player.feed_reward(50 + winning_player.kill_bonus)
                winning_player.update_game_over_training_diagnostics("wins")
            if loosing_player.is_ai_player:
                loosing_player.feed_reward(-50 + loosing_player.kill_bonus)
                loosing_player.update_game_over_training_diagnostics("losses")

        if winning_player == self.player2:
            loosing_player = self.player1
            if winning_player.is_ai_player:
                winning_player.feed_reward(50 + winning_player.kill_bonus)
                winning_player.update_game_over_training_diagnostics("wins")
            if loosing_player.is_ai_player:
                loosing_player.feed_reward(-50 + loosing_player.kill_bonus)
                loosing_player.update_game_over_training_diagnostics("losses")


    def is_player_one_turn(self):
        return self.current_player == self.player1

    def is_player_two_turn(self):
        return self.current_player == self.player2

    def player_one_won(self):
        return self.board.winner == self.player1

    def player_two_won(self):
        return self.board.winner == self.player2

    # def start(self):
    #     self.game_state = GameState.PLAYING

    def reset(self):

        """
        Reset the game back to a fresh starting state.

        - Clears the board
        - Clears AI episode memory (states visited this game)
        - Sets the turn back to player1
        - Returns the game to PLAYING
        """
        # self.game_state = GameState.START
        self.game_state = GameState.PLAYING
        self.current_player = self.player1
        self.board.reset()
        if self.player1.is_ai_player:
            self.player1.reset()
        if self.player2.is_ai_player:
            self.player2.reset()












