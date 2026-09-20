# MVHS CS Authorship Authenticity Statement:
# I affirm that all code in this submission was written by me.
# AI tools, if used, were used only for concept explanations, debugging interpretation, or syntax clarification.
# No AI-generated or AI-modified code was used.
# I understand that submitting false authorship statement is an academic integrity violation.

########################################################################################################################
###                                            ML RL Honey Defender                                                  ###
########################################################################################################################
import math
from collections.abc import Sequence # python -m src.main   to run
from enum import Enum

import pygame
from pygame import mouse

from .constants import FRAME_RATE
from .utilities import draw_text, \
    draw_button, draw_polygon, load_sfx, play_music, load_image, draw_image, draw_rect_center, _get_font

from . import constants
from .ai_player import AIPlayer
from .game_manager import GameManager, GameState
from .human_player import HumanPlayer

# EXTRA THINGS TO DO IF THERES TIME AND YOUR WAITING FOR THE OTHER PERSON

pygame.init()
window = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
pygame.display.set_caption('Honey Defender')
move_delay = 1 * FRAME_RATE

# region Global Gameplay Variables -------------------------------------------------------------------------------------
# Application modes
class Mode(Enum):
    # Two AI players train by playing against each other. No visuals are rendered to the screen.
    # This is the fastest training method and should be used when developing.
    HEADLESS_TRAINING = 0

    # Two AI players train by playing against each other. Visuals are rendered to the screen.
    # AI player will choose a move each frame. The see the training set FRAME_RATE in constants
    # file to a low number, (example FRAME_RATE = 2),
    # This training method should only be used to see the training in action (showcasing).
    TRAINING = 1

    # One human player (player 1) and one AI player (player 2). AI player will use policy defined by
    # POLICY_FILE in constants file. AI will not train.
    HUMAN_PLAY_AI = 2

    # Two Human players
    HUMAN_PLAY_HUMAN = 3

# Set the current mode here
# mode = Mode.HUMAN_PLAY_HUMAN
mode = None

def setup_game(selected_mode: Mode) -> None:
    global mode, player1, player2, game_manager, episode_count, player_move_input, reset_button
    mode = selected_mode
    if mode == Mode.HEADLESS_TRAINING:
        player1 = AIPlayer(True)
        player2 = AIPlayer(False)
    elif mode == Mode.TRAINING:
        player1 = AIPlayer(True)
        player2 = AIPlayer(False)
    elif mode == Mode.HUMAN_PLAY_AI:
        player1 = HumanPlayer(True)
        player2 = AIPlayer(False)
        player2.load_policy()
    else:
        player1 = HumanPlayer(True)
        player2 = HumanPlayer(False)
    game_manager = GameManager(player1, player2)
    # game_manager.start()
    episode_count = 0
    player_move_input = None
    reset_button = None

# if mode == Mode.HEADLESS_TRAINING:
#     player1 = AIPlayer(True)
#     player2 = AIPlayer(False)
# elif mode == Mode.TRAINING:
#     player1 = AIPlayer(True)
#     player2 = AIPlayer(False)
# elif mode == Mode.HUMAN_PLAY_AI:
#     player1 = HumanPlayer(True)
#     player2 = AIPlayer(False)
#     player2.load_policy()
# else:
#     player1 = HumanPlayer(True)
#     player2 = HumanPlayer(False)

# game_manager = GameManager(player1, player2)
# episode_count = 0
# player_move_input = None

# music
gone_fishin = load_sfx("gone_fishin.mp3")
play_music("gone_fishin.mp3")

# images
beedrill = load_image("beedrill.png")
ursaring = load_image("ursaring.png")

start_comb = load_image("start_comb.png")

# Start button for Human players to restart game
# start_button = "s"
# Reset button for Human players to restart game
reset_button = "r"

# endregion ------------------------------------------------------------------------------------------------------------

def animate() -> None:
    if game_manager.game_state == GameState.GAME_OVER:
        return
    global player_move_input,episode_count,move_delay

    if move_delay < 0 or constants.IGNORE_DELAY:
        move_delay = FRAME_RATE/2
        # Update game state via game manager
        game_manager.update(player_move_input)

    # Clear any human player inputs that were applied this frame
    player_move_input = None

    move_delay -= 1
    # print(move_delay)
    # If AI is training, automatically restart next game. After all training episodes save the learned AI policy
    if (mode == Mode.HEADLESS_TRAINING or mode == Mode.TRAINING) and game_manager.game_state == GameState.GAME_OVER:
        game_manager.reset()
        episode_count += 1
        if episode_count >= constants.EPISODES:
            if game_manager.player1.is_ai_player:
                game_manager.player1.save_policy()
            if game_manager.player2.is_ai_player:
                game_manager.player2.save_policy()


def paint() -> None:
    # if game_manager.game_state == GameState.START:
    #     draw_start_screen()
    #     return
    draw_game_board()
    draw_player_moves()
    # draw_cursor()

    if game_manager.game_state == GameState.PLAYING:
        if game_manager.is_player_one_turn():
            draw_player_one_turn()
        else:
            draw_player_two_turn()

    elif game_manager.game_state == GameState.GAME_OVER:
        draw_winner()
        draw_reset_button()


def draw_game_board() -> None:

    """
    Draws the empty Tic-Tac-Toe game board. (two vertical and two horizontal lines)
    """
    # tile_num = 0
    for hex_center in constants.HEX_LIST:
        draw_polygon(window, constants.HEXAGON_SHAPE, hex_center, constants.COLOR_ORANGE, 0, 1,constants.COLOR_YELLOW)
        # draw_text(window, str(tile_num), 20, constants.COLOR_BLACK, hex_center)
        # tile_num += 1 # count the tilesum



def draw_player_moves() -> None:

    """
    Draw all moves from both players on the board.
    """

    for i in range(len(constants.HEX_LIST)):
        # if type(game_manager.board.game_board[i]) is not int:
        #     return
        if game_manager.board.game_board[i] == game_manager.player1.identifier:
            # draw_text(window, "X", 50, constants.PLAYER_1_COLOR, constants.HEX_LIST[i])
            draw_image(window, ursaring, constants.HEX_LIST[i],0,constants.CELL_SIZE*.001)
        elif game_manager.board.game_board[i] == game_manager.player2.identifier:
            # draw_text(window, "0", 50, constants.PLAYER_2_COLOR, constants.HEX_LIST[i])
            draw_image(window, beedrill, constants.HEX_LIST[i],0,constants.CELL_SIZE*.001)
        # ARROW DRAWING BELOW
        # if the current player is not an AI and they are, and you are in the 2nd clicking phase
        if not game_manager.current_player.is_ai_player and not game_manager.current_player.selectingTile and game_manager.current_player.select_tile is not None:
        #draw the arrows, based off player turn
        # draw an arrow for all dirrections that are real tiles
            color = constants.COLOR_BLACK
            if game_manager.is_player_one_turn():
                color = constants.PLAYER_1_COLOR
            else:
                color = constants.PLAYER_2_COLOR
            for i in range(6):
                    possible_hexagon_center = ((constants.HEX_LIST[game_manager.current_player.select_tile][0] + constants.direction_patterns[i + 1][0]),(constants.HEX_LIST[game_manager.current_player.select_tile][1] + constants.direction_patterns[i + 1][1]))
                    if possible_hexagon_center in constants.HEX_LIST:
                        draw_polygon(window, constants.ARROW_SHAPE,(constants.HEX_LIST[game_manager.current_player.select_tile][0]+round(constants.direction_patterns[i + 1][0]/2),constants.HEX_LIST[game_manager.current_player.select_tile][1]+round(constants.direction_patterns[i + 1][1]/2)), color,constants.direction_patterns[i + 1][2], 1, constants.COLOR_BLACK)





def draw_player_one_turn() -> None:
    draw_text(window, "Player One", 24, constants.PLAYER_1_COLOR, (int(constants.WINDOW_WIDTH * 0.12), 18),color2=constants.COLOR_WHITE)


def draw_player_two_turn() -> None:
    draw_text(window, "Player Two", 24, constants.PLAYER_2_COLOR, (int(constants.WINDOW_WIDTH * 0.12), 18),color2=constants.COLOR_WHITE)

# def draw_cursor() -> None:
#     mouse_pos = pygame.mouse.get_pos()

    # draw_text(window, "Mouse_Pos: "  + str(mouse_pos), 10,constants.COLOR_RED, mouse_pos)

    # draw_text(window,(str(mouse_pos) + str(HumanPlayer.choose_move(game_manager, mouse_pos))),10,constants.COLOR_RED,mouse_pos)
    # HumanPlayer.choose_move(game_manager, mouse_pos)


def draw_winner() -> None:

    if game_manager.player_one_won():
        winner_text = "Player One Wins!"
        color = constants.PLAYER_1_COLOR
    elif game_manager.player_two_won():
        winner_text = "Player Two Wins!"
        color = constants.PLAYER_2_COLOR
    else:
        winner_text = "Tie!"
        color = constants.COLOR_WHITE

    # int(constants.WINDOW_WIDTH * 0.5),int(constants.WINDOW_HEIGHT * 0.2)
    draw_rect_center(window,(int(constants.WINDOW_WIDTH * 0.5), 100),
                     (int(constants.WINDOW_WIDTH * 0.55),int(constants.WINDOW_HEIGHT * 0.2)),constants.COLOR_BLACK,transparent=150)
    draw_text(window, winner_text, 35, color, (int(constants.WINDOW_WIDTH * 0.5), 100),color2=constants.COLOR_WHITE)

def draw_reset_button() -> None:

    global reset_button
    reset_button = draw_button(window, "Reset", (int(constants.WINDOW_WIDTH * 0.5), constants.WINDOW_HEIGHT - 100),
                               30, constants.COLOR_RED_BROWN, constants.COLOR_LIGHT_BLUE,(140,50))

# def draw_start_screen() -> None:
#     global start_button
#     start_button = draw_button(window, "Start", (int(constants.WINDOW_WIDTH * 0.5),constants.WINDOW_HEIGHT - 100),
#                                30, constants.COLOR_RED_BROWN, constants.COLOR_LIGHT_BLUE)
#     draw_text(window,"Honey Defender",70,constants.COLOR_ORANGE,
#               (constants.BOARD_CENTER_X,int(constants.WINDOW_HEIGHT*0.1)),color2=constants.COLOR_YELLOW)
#     draw_image(window, ursaring, (int(constants.WINDOW_WIDTH*.2),int(constants.WINDOW_HEIGHT*.8)),0, .4)
#     draw_image(window, beedrill, (int(constants.WINDOW_WIDTH*.8),int(constants.WINDOW_HEIGHT*.8)),0, .4)
#     draw_image(window,start_comb,(constants.BOARD_CENTER_X,constants.BOARD_CENTER_Y-30),0,.65)

# region User Input ----------------------------------------------------------------------------------------------------

def process_mouse_event(event: pygame.event.Event) -> None:

    """
    This method is called when a mouse event occurs.

    :param event: The Pygame mouse event to process (MOUSEBUTTONDOWN, or MOUSEMOTION)
    """

    global player_move_input
    global reset_button, move_delay


    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if game_manager.game_state == GameState.GAME_OVER:
            if reset_button is not None and reset_button.collidepoint(event.pos):
                game_manager.reset()
                reset()
        elif game_manager.game_state == GameState.PLAYING:
                move_delay = -1
                x_pos, y_pos = mouse.get_pos()
                player_move_input = x_pos, y_pos
        # elif game_manager.game_state == GameState.START:
        #     if start_button is not None and start_button.collidepoint(event.pos):
        #         game_manager.start()



def process_key_event(event: pygame.event.Event) -> None:

    """
    This method is only called when a key event occurs.

    :param event: The Pygame key KEYDOWN event to process
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        game_manager.reset()
        reset()


def process_keys_held(keys: Sequence[bool]) -> None:

    """
    This method is called every frame. Used to get keys that are held over sequential frames
    :param keys:
    :return:
    """
    pass



# endregion

# region Game Update Loop ----------------------------------------------------------------------------------------------

def reset() -> None:
    # pass is what we put in a function when we have not implemented it yet.
    # After you add code to this method, delete the pass line of code.
    pass

########################################################################################################################
# You should not have to edit any of the code in the game update loop below
########################################################################################################################

def menu_screen() -> Mode:
    button_width, button_height = 300, 50
    # cx = constants.WINDOW_WIDTH // 2
    buttons = [
        ("Human vs Human", Mode.HUMAN_PLAY_HUMAN, (210, 480)),
        ("Human vs AI", Mode.HUMAN_PLAY_AI, (210, 550)),
        ("Training Visual", Mode.TRAINING, (590, 480)),
        ("Headless Training",  Mode.HEADLESS_TRAINING,  (590, 550)),
    ]
    window.fill(constants.COLOR_BLUE_GREEN)
    draw_text(window, "Honey Defender", 55, constants.COLOR_ORANGE,
              (constants.BOARD_CENTER_X, int(constants.WINDOW_HEIGHT * 0.1)), color2=constants.COLOR_YELLOW)
    draw_image(window, ursaring, (int(constants.WINDOW_WIDTH * .15), int(constants.WINDOW_HEIGHT * .55)), 0, .35)
    draw_image(window, beedrill, (int(constants.WINDOW_WIDTH * .85), int(constants.WINDOW_HEIGHT * .55)), 0, .35)
    draw_image(window, start_comb, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y - 30), 0, .65)

    frame_rate = int(constants.FRAME_RATE) or 60
    while True:
        pygame.time.delay(int(1000 / frame_rate))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for _, m, rect_center in buttons:
                    r = pygame.Rect(0, 0, button_width, button_height)
                    r.center = rect_center
                    if r.collidepoint(event.pos):
                        # game_manager.start()
                        return m

        mouse_x, mouse_y = mouse.get_pos()
        for label, _, rect_center in buttons:
            r = pygame.Rect(0, 0, button_width, button_height)
            r.center = rect_center
            hover = r.collidepoint(mouse_x, mouse_y)
            text_color = constants.COLOR_RED_BROWN
            background = constants.COLOR_YELLOW if hover else constants.COLOR_LIGHT_BLUE
            draw_button(window, label, rect_center, 22,text_color, background,
                        (button_width, button_height), corner_radius=8)

        pygame.display.flip()

def play_game():
    selected = menu_screen()
    setup_game(selected)
    reset()
    # set pygame favicon
    favicon = pygame.image.load('./assets/images/honeycomb.png')
    pygame.display.set_icon(favicon)
    # If training in headless mode then no rendering (pygame) is needed
    if mode == Mode.HEADLESS_TRAINING:
        # window.fill(constants.COLOR_BLACK)
        while episode_count < constants.EPISODES:
            # episode_count is updated in animate
            # window.fill(constants.COLOR_BLACK)
            animate()
        return

    run = True
    frame_rate = int(constants.FRAME_RATE)
    frame_rate = frame_rate if frame_rate > 0 else 15
    while run:

        # if game_manager.game_state == GameState.START:
        #     game_manager.reset()
        #     play_game()
        #     break

        # Limit the game to FRAME_RATE frames per second (delay in milliseconds).
        pygame.time.delay(int(1000 / frame_rate))


        # Handle all events from the previous frame.
        # Quit event - exit game loop
        # Mouse events: pass to mouse event input handler
        # Key events: pass to keyboard even input handler
        pygame_events = pygame.event.get()
        for pygame_event in pygame_events:
            if pygame_event.type == pygame.QUIT:
                run = False
            else:
                if pygame_event.type == pygame.MOUSEBUTTONDOWN or pygame_event.type == pygame.MOUSEBUTTONUP or pygame_event.type == pygame.MOUSEMOTION:
                    process_mouse_event(pygame_event)

                if pygame_event.type == pygame.KEYDOWN or pygame_event.type == pygame.KEYUP:
                    process_key_event(pygame_event)

        # Keys held: pass to keys held input handler
        process_keys_held(pygame.key.get_pressed())

        # Update the game state (position, collisions, and timers)
        window.fill(constants.COLOR_BLUE_GREEN)
        animate()

        # Render visuals
        paint()

        pygame.display.flip()

    pygame.quit()


# endregion

if __name__ == '__main__':
    play_game()
