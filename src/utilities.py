import math
import pygame
from pathlib import Path

from shapely.geometry.polygon import Polygon as Polygon
from shapely.geometry.point import  Point as Point

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / 'assets' / 'images'
SOUNDS_DIR = BASE_DIR / 'assets' / 'sounds'

font_cache = {}
sound_cache = {}

def load_image(image_file_name: str, default_scale: float = 1) -> pygame.Surface:

    """
    Loads an image file from IMAGE_DIR, optionally set the default scale.

    :param image_file_name:  File name of the image to load (example "rocket.png")
    :param default_scale: Multiplier applied to image size (1 = original size)

    :return: A pygame.Surface containing the image (and scaled). If loading fails a magenta placeholder is used
    """

    image_file = IMAGES_DIR / image_file_name
    try:

        surface = pygame.image.load(str(image_file)).convert_alpha()
        if default_scale == 1:
            return surface
        else:
            width, height = surface.get_size()
            new_scale = int(round(width * default_scale)), int(round(height * default_scale))
            return pygame.transform.smoothscale(surface, new_scale)
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"Unable to load {image_file_name}. Error: {e}")
        surface = pygame.Surface((100, 100))
        # Magenta fill color
        surface.fill((255, 0, 255))
        return surface


def draw_image(window: pygame.surface, surface: pygame.Surface, center: tuple[int, int], rot: float = 0, scale: float = 1) -> None:

    """
    Draw an image using a center position.

    :param window: The screen surface to draw on
    :param surface: The original surface (image) to draw
    :param center: position on the screen (window) where the center of the image (surface) will be placed
    :param rot: Rotation angle in degrees, positive values are counter-clockwise
    :param scale: Scale factor (1 = original size, smaller scale factor = smaller image)
    :return: None
    """

    image = pygame.transform.rotozoom(surface, rot, scale)
    rect = image.get_rect(center=center)
    window.blit(image, rect)

def create_shape(sides: int = 6, side_length: float = 1,center: tuple[int,int] = (0,0)) -> list:
    vertices = []
    for i in range(sides):
        angle_rad = math.radians(360/sides * i)
        x = int(side_length * math.cos(angle_rad) + center[0])
        y = int(side_length * math.sin(angle_rad) + center[1])
        vertices.append((x, y))
        # print()
    # create the shape
    return vertices
def bounding_polygon(sides: int = 6, side_length: float = 1 , center: tuple[int, int]=(0,0), mouse_pos: tuple[int,int]=(0,0)) -> bool:
    polygon_shape = Polygon(create_shape(sides, side_length, center))
    inside = polygon_shape.contains(Point(mouse_pos))
    return inside

def draw_polygon(window: pygame.surface, coords: list[tuple[int, int]], center: tuple[int, int], color: tuple[int, int, int], rot: float = 0, scale: float = 0, OUTLINE_COLOR=None,width: int = 5) -> None:

    """
    Draw a polygon using a center position, optional rotation, and scale.

    :param window: The screen surface to draw on
    :param coords: local polygon points defined around (0, 0)
    :param center: (x, y) screen position where the polygon will be centered
    :param color: RGB color of the polygon
    :param rot: Rotation angle in degrees, positive values are counter-clockwise
    :param scale: Scale multiplier (1 = original size, 0.5 = half, 2 = double)
    :return:
    """

    # position x, y points in coords so they are centered around center
    positioned_points = [(x + center[0], -y + center[1]) for x, y in coords]

    # Scale points around the center. Keep polygon anchored to the same center as it grow/shrinks
    scaled_points = []
    for x, y in positioned_points:
        x_scaled = math.floor((scale * (x - center[0])) + center[0])
        y_scaled = math.floor((scale * (y - center[1])) + center[1])
        scaled_points.append((x_scaled, y_scaled))

    # Rotate points around center
    # https://stackoverflow.com/questions/75116101/how-to-make-rotate-polygon-on-key-in-pygame
    pp = pygame.math.Vector2((center[0], center[1]))
    rotated_points = [(pygame.math.Vector2(x, y) - pp).rotate(rot) + pp for x, y in scaled_points]

    pygame.draw.polygon(window, color, rotated_points)
    if OUTLINE_COLOR is not None:
        pygame.draw.polygon(window,OUTLINE_COLOR, rotated_points, width)


def draw_rect_center(window: pygame.surface, center: tuple[int,int], size: tuple[int,int], color: tuple[int, int, int], rot: float = 0, border_width: int = 0,transparent: int=None) -> None:

    """
    Draw a rectangle center using a center position, optional rotation, and scale.

    Note: You can still draw a pygame.Rect (which is normally defined by its top-left corner).
    Example: https://www.geeksforgeeks.org/python/how-to-draw-rectangle-in-pygame/

    :param window: The screen surface to draw on
    :param center: (x, y) screen position where the rectangle will be centered
    :param size: (width, height) size of the rectangle in pixels
    :param color: RGB color of the rectangle
    :param rot: Rotation angle in degrees, positive values are counter-clockwise
    :param border_width: 0 draws a filled rect. >0 draws an outline of that thickness.
    :return:
    """

    temp_surface = pygame.Surface(size, pygame.SRCALPHA)
    temp_surface.set_alpha(transparent)
    pygame.draw.rect(temp_surface, color, pygame.Rect(0,0,size[0],size[1]), border_width)
    rotated = pygame.transform.rotate(temp_surface, rot)
    rect = rotated.get_rect(center=center)
    window.blit(rotated, rect)


def draw_ellipse_centered(window: pygame.surface, center: tuple[int,int], size: tuple[int,int], color, border_width = 0) -> None:

    """
    Draw an ellipse centered using a center position, optional rotation, and scale.

    Note: You can still draw a pygame.ellipse https://www.tutorialspoint.com/pygame/pygame_drawing_shapes.htm

    :param window: The screen surface to draw on
    :param center: (x, y) screen position where the ellipse will be centered
    :param size: (width, height) size of the ellipse in pixels
    :param color: RGB color of the ellipse
    :param border_width: 0 draws a filled ellipse. >0 draws an outline of that thickness.
    :return:
    """

    rect = pygame.Rect(0, 0, size[0], size[1])
    rect.center = center
    pygame.draw.ellipse(window, color, rect, border_width)


def _get_font(font_name, size):

    """
    Get a font object by name, You do not need to call this function directly in your Space Invader code.
    :param font_name: Name of system font
    :param size:  Size of font in pixels
    :return: A pygame.font.Font object
    """
    key = (font_name, size)

    # Create the font of not cached yet. Ensure we only create each font at the same size once
    if key not in font_cache:
        if font_name is None:
            font_cache[key] = pygame.font.Font(None, size)
        else:
            font_cache[key] = pygame.font.SysFont(font_name, size)

    return font_cache[key]


def draw_text(window: pygame.display, text: str, size: int, color: tuple[int, int, int], center: tuple[int, int], rot = 0, font_name="Ravie",color2: tuple[int, int, int]=None, shift_x: float=1.2, shift_y: int=1.5) -> None:

    """
    Draw a text using a center position.

    :param window: The screen surface to draw on
    :param text: Text to draw
    :param size: size of the text
    :param color: RGB color of the text
    :param center: (x, y) screen position where the text will be centered
    :param rot: Rotation angle in degrees, positive values are counter-clockwise
    :param font_name: Name of system font
    :return:
    """
    font = _get_font(font_name, size)
    if color2 is not None:
        text_surface = font.render(text, True, color2)
        if rot != 0:
            text_surface = pygame.transform.rotate(text_surface, rot)

        font_rect = text_surface.get_rect(center=(center[0]+shift_x, center[1]+shift_y))
        window.blit(text_surface, font_rect)
    text_surface = font.render(text, True, color)
    if rot != 0:
        text_surface = pygame.transform.rotate(text_surface, rot)

    font_rect = text_surface.get_rect(center=center)
    window.blit(text_surface, font_rect)

def draw_button(window: pygame.Surface, text:str, center: tuple[int,int], text_size: int, text_color: tuple[int, int, int],
                background_color: tuple[int, int, int], padding: tuple[int, int]=(10, 10), font_name: str = "Ravie", corner_radius: int = 0) -> pygame.Rect:

    """
    Draw a simple UI button. Returns to button rect. See example folder on how to detect button click

    :param window: The screen surface to draw on
    :param text: Text to draw
    :param center: (x, y) screen position where the button will be centered
    :param text_size: size of the text
    :param text_color: RGB color of the text
    :param background_color: RGB color of the button (under text)
    :param padding: (x, y) padding around the text
    :param font_name: Name of system font
    :param corner_radius: radius of the button rounded corners (0 = square corners)
    :return: pygame.Rect object
    """

    font = _get_font(font_name, text_size)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()

    # button_width = text_rect.width + padding[0] * 2
    # button_height = text_rect.height + padding[1] * 2
    button_width = padding[0]
    button_height = padding[1]
    button_rect = pygame.Rect(0, 0, button_width, button_height)
    button_rect.center = center

    pygame.draw.rect(window, background_color, button_rect, border_radius=corner_radius)

    text_rect.center = button_rect.center
    window.blit(text_surface, text_rect)
    return button_rect



def load_sfx(sfx_file_name: str, volume: float = 1.0) -> pygame.mixer.Sound|None:

    """
    Load and cache a sound from the SOUNDS_DIR folder
    :param sfx_file_name: file name of the sound file in SOUNDS_DIR (assets/sounds/)
    :param volume: default volume to cache
    :return: pygame.mixer.Sound object to play the sound file
    """

    try:
        if sfx_file_name not in sound_cache:
            path = SOUNDS_DIR / sfx_file_name
            sound_cache[sfx_file_name] = pygame.mixer.Sound(str(path))

        sound = sound_cache[sfx_file_name]
        volume_clamped = max(0.0, min(1.0, volume))
        sound.set_volume(volume_clamped)
        return sound
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"Unable to play sound:{sfx_file_name}. Error: {e}")
        return None


def play_sfx(sfx_file_name: str, volume: float = 1.0) -> None:

    """
    Play a sound loaded from the SOUNDS_DIR folder (must call load_sfx() first)

    :param sfx_file_name: file name of the sound file in SOUNDS_DIR (assets/sounds/)
    :param volume: volume of sound
    :return:
    """
    sound = None
    try:
        sound = load_sfx(sfx_file_name)
        if sound is None:
            raise pygame.error
        sound.play()
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"Unable to play sound:{sound}. Error: {e}")


def play_music(music_file_name: str, volume: float = 1.0, loops: int = -1) -> None:

    """
    Play background sounds from the SOUNDS_DIR folder (must call load_sfx() first)

    :param music_file_name: file name of the sound file in SOUNDS_DIR (assets/sounds/)
    :param volume: volume of sounds
    :param loops: number of extra times to repeat (-1 = loop forever, 0 = play once)
    :return:
    """

    path = SOUNDS_DIR / music_file_name
    try:
        pygame.mixer.music.load(path)
        volume_clamped = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume_clamped)
        pygame.mixer.music.play(loops=loops)
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"Unable to play sounds:{path}. Error: {e}")



def stop_music():

    """
    Stop any playing sounds
    :return:
    """
    pygame.mixer.music.stop()

