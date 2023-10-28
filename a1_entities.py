"""CSC148 Assignment 1 - People and Elevators

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains classes for the two basic entities in this simulation:
people and elevators. We have provided outlines of these two classes
for you; you are responsible for implementing these two classes so that they
work with the rest of the simulation.

You may NOT change any existing attributes, or the interface for any public
methods we have provided. However, you can add new PRIVATE attributes,
and of course you'll have to implement the methods we've provided, as well
as add your own methods to complete this assignment.

Person and Elevator each inherit from a "sprite" class found in visualizer.py.
This is to enable their instances to be visualized properly.
You may not change visualizer.py, but are responsible for reading the documentation
to understand these classes, as well as the abstract methods your classes must
implement.
"""
from __future__ import annotations
from python_ta.contracts import check_contracts
from a1_visualizer import PersonSprite, ElevatorSprite


@check_contracts
class Person(PersonSprite):
    """A person in the elevator simulation.

    Instance Attributes:
    - start: the floor this person started on
    - target: the floor this person wants to go to
    - wait_time: the number of rounds this person has been waiting

    Representation Invariants:
    - self.start >= 1
    - self.target >= 1
    - self.start != self.target
    - self.wait_time >= 0
    """
    start: int
    target: int
    wait_time: int

    def __init__(self, start: int, target: int) -> None:
        """Initialize a person with the given start and target floor.

        A person's waiting time always starts at 0.

        Preconditions:
        - start >= 0
        - target >= 0

        NOTE: Initialize all Person instance attributes BEFORE calling PersonSprite.__init__.
        This is because the PersonSprite initializer will call get_anger_level, which
        should depend on self.wait_time.
        """
        self.start = start
        self.target = target
        self.wait_time = 0
        super().__init__()

    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
        - Level 0: waiting 0-2 rounds
        - Level 1: waiting 3-4 rounds
        - Level 2: waiting 5-6 rounds
        - Level 3: waiting 7-8 rounds
        - Level 4: waiting >= 9 rounds

        Note: this method overrides PersonSprite.get_anger_level, used when
        visualizing a person (how?).

        >>> my_person = Person(1, 5)
        >>> my_person.wait_time = 5
        >>> my_person.get_anger_level()
        2
        """
        if 0 <= self.wait_time <= 2:
            return 0
        elif 3 <= self.wait_time <= 4:
            return 1
        elif 5 <= self.wait_time <= 6:
            return 2
        elif 7 <= self.wait_time <= 8:
            return 3
        else:
            return 4

    def __repr__(self) -> str:
        """Return a string representation of this Person.

        This function is a special method that displays a custom string when an object
        of this type is evaluated in the Python console. It is provided for you for
        testing purposes; please don't change it!

        >>> my_person = Person(1, 5)
        >>> my_person
        Person(start=1, target=5, wait_time=0)
        """
        return f'Person(start={self.start}, target={self.target}, wait_time={self.wait_time})'


@check_contracts
class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Remember to add additional documentation to this class docstring
    as you add new attributes (and representation invariants).

    Instance Attributes:
    - capacity: The maximum number of people on this elevator
    - current_floor: The floor this elevator is on
    - passengers:
        The passengers of this elevator (this attribute also appears in
        the ElevatorSprite class)
    - target_floor: the floor this elevator is headed towards

    Representation Invariants:
    - self.current_floor >= 1
    - self.capacity > 0
    - len(self.passengers) <= self.capacity
    - self.target_floor >= 1
    """
    capacity: int
    current_floor: int
    passengers: list[Person]
    target_floor: int

    def __init__(self, capacity: int) -> None:
        """Initialize a new elevator with the given capacity.

        Elevators always start with a current and target floor of 1, and no passengers.

        Preconditions:
        - capacity > 0
        """
        self.capacity = capacity
        self.current_floor = 1
        self.passengers = []
        self.target_floor = 1
        super().__init__()

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

        The value returned should be a float between 0.0 (empty) and 1.0 (full).

        Note: this method overrides ElevatorSprite.fullness, used when
        visualizing an elevator (how?).

        >>> my_elevator = Elevator(10)
        >>> my_elevator.fullness()
        0.0
        """
        return len(self.passengers) / self.capacity


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # Uncomment the python_ta lines below and run this module.
    # This is different that just running doctests! To run this file in PyCharm,
    # right-click in the file and select "Run a1_entities" or "Run File in Python Console".
    #
    # python_ta will check your work and open up your web browser to display
    # its report. For full marks, you must fix all issues reported, so that
    # you see "None!" under both "Code Errors" and "Style and Convention Errors".
    # TIP: To quickly uncomment lines in PyCharm, select the lines below and press
    # "Ctrl + /" or "⌘ + /".
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['a1_visualizer'],
        'max-line-length': 100
    })
