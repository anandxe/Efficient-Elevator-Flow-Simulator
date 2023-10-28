"""CSC148 Assignment 1 - Visualizer

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains the Visualizer class, which is responsible for interacting
with Pygame, the graphics library we're using for this assignment.
There's quite a bit in this file, but you aren't responsible for most of it.

DO NOT CHANGE ANY CODE IN THIS FILE. You don't need to for this assignment,
and in fact you aren't even submitting this file!
"""
from __future__ import annotations
from enum import Enum
import random
import time
from typing import Any

import pygame


###############################################################################
# Public sprite classes (you need to read these)
###############################################################################
class ElevatorSprite(pygame.sprite.Sprite):
    """Sprite representing an elevator.

    Instance Attributes:
    - image: the Pygame surface on which to draw this sprite
    - rect: the rectangle representing the dimensions of this sprite
    - passengers:
        a list of the PersonSprites currently on this elevator
        NOTE: since Person is a subclass of PersonSprite, you can (and should)
        add Person objects to this list; see the add_passenger method below
    """
    image: pygame.Surface
    rect: pygame.Rect
    passengers: list[PersonSprite]

    def __init__(self) -> None:
        """Initialize a new ElevatorSprite."""
        super().__init__()
        self.image = pygame.Surface([ELEVATOR_WIDTH, ELEVATOR_HEIGHT])
        self.image.fill(GREEN)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.passengers = []

    def update(self) -> None:
        """Update this elevator's image based on its fullness."""
        pygame.draw.rect(self.image, GREEN,
                         [0, 0, ELEVATOR_WIDTH, ELEVATOR_HEIGHT])
        pygame.draw.rect(self.image, DARK_GREEN,
                         [0, ELEVATOR_HEIGHT * (1 - self.fullness()),
                          ELEVATOR_WIDTH, ELEVATOR_HEIGHT])

    def add_passenger(self, person: PersonSprite) -> None:
        """Add a passenger to this elevator."""
        self.passengers.append(person)

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

        The value returned should be a float between 0.0 (completely empty) and
        1.0 (completely full).
        """
        raise NotImplementedError


class PersonSprite(pygame.sprite.Sprite):
    """Sprite representing a person.

    Instance Attributes:
    - height: the height of the person sprite
    - width: the width of the person sprite
    - image: the Pygame surface on which to draw this sprite
    - rect: the rectangle representing the dimensions of this sprite

    Representation Invariants:
    - self.height >= 0
    - self.width >= 0
    """
    height: int
    width: int
    image: pygame.Surface
    rect: pygame.Rect

    def __init__(self) -> None:
        """Initialize a new person sprite."""
        super().__init__()
        self.width, self.height = PERSON_WIDTH, PERSON_HEIGHT
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.bottom = 0
        self.rect.centerx = random.randint(-2, 2)

    def load_image(self) -> Any:
        """Load the image for this sprite and redraws it
        Lower indices are happier :)
        """
        image = pygame.image.load(FIGURES[self.get_anger_level()])
        return pygame.transform.scale(image, (self.width, self.height))

    def get_anger_level(self) -> int:
        """Return the anger level of this sprite.

        This determines the image used to render this sprite.

        Anger level must be an integer between 0 and 4, inclusive.
        (0 means not at all angry, 4 is very angry)
        """
        raise NotImplementedError


###############################################################################
# Visualizer and Direction class
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is used as input for Visualizer.show_elevator_moves.

    The possible values you'll use in your Python code are:
    - Direction.UP
    - Direction.DOWN
    - Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class Visualizer:
    """Visualizer for the current state of a simulation.

    All attributes of this class are private; you are not responsible for
    understanding them, and they are left undocumented.
    """
    _visualize: bool
    _num_elevators: int
    _num_floors: int
    _clock: pygame.time.Clock
    _screen: pygame.Surface
    _sprite_group: pygame.sprite.Group
    _stats_group: pygame.sprite.Group

    def __init__(self,
                 elevators: list[ElevatorSprite],
                 num_floors: int,
                 visualize: bool) -> None:
        """Initialize this visualization.

        If visualize is False, this instance does nothing.
        """
        self._visualize = visualize
        if not self._visualize:
            return

        self._num_elevators = len(elevators)
        self._num_floors = num_floors

        # pygame stuff
        pygame.init()
        self._clock = pygame.time.Clock()

        self._screen = pygame.display.set_mode(
            (WIDTH, self._total_height()), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._screen.fill(WHITE)

        # Contains all sprites in the simulation
        self._sprite_group = pygame.sprite.Group()
        self._stats_group = pygame.sprite.Group()

        self._setup_sprites(elevators)
        # Initial render.
        self.render()

    def render_header(self, round_num: int) -> None:
        """Render text displaying the round number for this simulation."""
        if not self._visualize:
            return
        self._stats_group.remove(list(self._stats_group))
        self._stats_group.add(_StatLine(0, f'Round {round_num}'))
        for sprite in self._sprite_group:
            if isinstance(sprite, PersonSprite):
                sprite.image = sprite.load_image()
        self.render()

    def render(self) -> None:
        """Draw the current state of the simulation to the screen.
        """
        if not self._visualize:
            return

        # Need this on OSX due to pygame bug
        pygame.event.peek(0)

        self._screen.fill(WHITE)
        self._sprite_group.draw(self._screen)
        self._stats_group.draw(self._screen)
        self._clock.tick(FPS)
        pygame.display.flip()

    def show_arrivals(self,
                      arrivals: dict[int, list[PersonSprite]]) -> None:
        """Show new arrivals."""
        if not self._visualize:
            return

        x = 10
        for floor, people in arrivals.items():
            y = self._get_y_of_floor(floor)
            for person in people:
                person.rect.bottom = y
                person.rect.centerx = x + random.randint(-3, 3)
                self._sprite_group.add(person)
        self.render()

    def show_boarding(self, person: PersonSprite,
                      elevator: ElevatorSprite) -> None:
        """Show boarding of the given person onto the given elevator.

        Preconditions:
        - the given person is on the same floor as the elevator.
        """
        if not self._visualize:
            return

        from_x = 10
        target_x = elevator.rect.centerx + random.randint(-3, 3)

        for frame in range(21):  # Move in 20 seconds
            person.rect.centerx = from_x + (target_x - from_x) * frame // 20
            self.render()

        elevator.update()
        self.render()

    def show_disembarking(self, person: PersonSprite,
                          elevator: ElevatorSprite) -> None:
        """Show disembarking of the given person from the given elevator."""
        if not self._visualize:
            return

        from_x = person.rect.centerx
        target_x = WIDTH - 10

        elevator.update()

        for frame in range(21):  # Move in 20 seconds
            x = from_x + (target_x - from_x) * frame // 20
            person.rect.centerx = x
            self.render()

    def show_elevator_moves(self,
                            elevators: list[ElevatorSprite],
                            directions: list[Direction]) -> None:
        """Show elevator moves. Note that all the elevators move at once."""
        if not self._visualize:
            return

        for _ in range(20):  # Move in 20 seconds
            for elevator, direction in zip(elevators, directions):
                if direction == Direction.UP:
                    step = - FLOOR_HEIGHT / 20
                elif direction == Direction.DOWN:
                    step = FLOOR_HEIGHT / 20
                else:
                    step = 0
                elevator.rect.bottom += step
                for passenger in elevator.passengers:
                    passenger.rect.bottom += step

            self.render()

    def wait(self, wait_time: int) -> None:
        """Wait for the specified amount of time, in seconds.

        Only occurs if self._visualize is True, otherwise there's no need to
        wait.
        """
        if self._visualize:
            time.sleep(wait_time)

    def wait_for_exit(self) -> None:
        """Wait until the user exits the pygame window (by pressing the close button).

        Does nothing if self._visualize is False.
        """
        if self._visualize:
            # This waits for you to close the pygame window (by pressing the "close" button)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.display.quit()
                        return

    ###########################################################################
    # Private helper methods (you don't need to worry about these)
    ###########################################################################
    def _setup_sprites(self, elevators: list[ElevatorSprite]) -> None:
        """Set up the initial sprites for this visualization.

        Position them on the screen and spaces them based on:
        - Size of the screen
        - Number of each item
        """
        for i in range(1, self._num_floors + 1):
            y = self._get_y_of_floor(i)
            floor = _FloorSprite(WIDTH, FLOOR_HEIGHT, y)
            floor_num = _FloorNum(y - 20, str(i))
            self._sprite_group.add(floor_num)
            self._sprite_group.add(floor)

        for i, elevator in enumerate(elevators):
            elevator.rect.centerx =\
                (i + 1) * WIDTH // (self._num_elevators + 1)
            elevator.rect.bottom = self._total_height() - FLOOR_BORDER_HEIGHT

            self._sprite_group.add(elevator)

    def _total_height(self) -> int:
        """Return the screen height for this visualization."""
        return self._num_floors * FLOOR_HEIGHT + STAT_WINDOW_HEIGHT

    def _get_y_of_floor(self, floor: int) -> int:
        """Return the y-coordinate of the given floor."""
        assert self._num_floors >= floor >= 1, f'{self._num_floors}, {floor}'
        return (
            self._total_height()
            - (floor - 1) * FLOOR_HEIGHT
            - FLOOR_BORDER_HEIGHT
        )


###############################################################################
# Visualization constants (you don't need to worry about these)
###############################################################################
# Colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)

# Dimensions for various objects
WIDTH = 900               # Screen width
STAT_WINDOW_HEIGHT = 100  # Space at the top for stats and messages
FLOOR_HEIGHT = 100        # The height of each floor (including the border)
FLOOR_BORDER_HEIGHT = 10  # The height of the border

ELEVATOR_HEIGHT = 66      # Elevator height
ELEVATOR_WIDTH = 44       # Elevator width

PERSON_HEIGHT = 50        # Person height
PERSON_WIDTH = 32         # Person width

# Frames per second based on config speed
FPS = 60

# Images for people
FIGURES = [f'images/person{i}.png' for i in range(1, 6)]

# Fonts
FONT_HEIGHT = 30
pygame.init()  # Need to call this before creating a new font
COMIC_SANS = pygame.font.SysFont('Comic Sans MS', FONT_HEIGHT)


###############################################################################
# Private sprite classes (you don't need to worry about these)
###############################################################################
class _FloorSprite(pygame.sprite.Sprite):
    """Sprite that draws a floor of the building.
    """
    def __init__(self, width: int, height: int, y: int) -> None:
        """Initialize a sprite representing a floor of the building."""
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.rect(self.image, BLUE, [0, 0, width, FLOOR_BORDER_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.top = y


class _FloorNum(pygame.sprite.Sprite):
    """Text Sprite to Label the floor number.
    """
    def __init__(self, floor_y: int, text: str) -> None:
        """Initialize a floor number text sprite."""
        super().__init__()
        self.floor_font = COMIC_SANS
        self.image = self.floor_font.render(text, True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = floor_y
        self.rect.right = WIDTH - 20


class _StatLine(pygame.sprite.Sprite):
    """Text Sprite for displaying some text.
    """
    def __init__(self, y: int, text: str) -> None:
        """Initialize a text sprite."""
        super().__init__()
        self.floor_font = COMIC_SANS
        self.image = self.floor_font.render(text, True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = 5
