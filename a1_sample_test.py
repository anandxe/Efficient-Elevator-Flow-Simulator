"""CSC148 Assignment 1: Sample tests

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains sample tests for Assignment 1.

Warning: This is an extremely incomplete set of tests!
Add your own to practice writing tests and to be confident your code is correct.

Note: this file is for support purposes only, and is not part of your submission.
"""
from a1_entities import Person, Elevator
from a1_algorithms import SingleArrivals, FileArrivals, EndToEndLoop, FurthestFloor
from a1_simulation import Simulation


###############################################################################
# Sample tests for Parts 1 and 2
###############################################################################
def test_person_initializer() -> None:
    """Test the person initializer."""
    person = Person(1, 5)
    assert person.start == 1
    assert person.target == 5
    assert person.wait_time == 0


def test_simulation_initializer_num_floors() -> None:
    """Test the simulation initializer for the num_floors attribute."""
    config = get_example_config()  # See "Helpers" at the bottom of this file
    simulation = Simulation(config)

    assert simulation.num_floors == 6


def test_simulation_initializer_elevators() -> None:
    """Test the simulation initializer for the elevators attribute."""
    config = get_example_config()
    simulation = Simulation(config)

    assert len(simulation.elevators) == 2
    for elevator in simulation.elevators:
        assert elevator.capacity == 2


###############################################################################
# Sample tests for Part 3
###############################################################################
def test_single_arrivals_example() -> None:
    """Test the SingleArrivals with the given example."""
    arrival_generator = SingleArrivals(4)
    expected_targets = [2, 3, 4, 2, 3, 4, 2]

    actual_targets = []
    for round_num in range(7):
        result = arrival_generator.generate(round_num)
        assert 1 in result  # Checks that result has the right key

        assert len(result[1]) == 1  # Checks that there's only one person generated

        person = result[1][0]
        actual_targets.append(person.target)

    assert actual_targets == expected_targets


def test_end_to_end_loop_floor1() -> None:
    """Test the EndToEndLoop algorithm when there is an elevator on floor 1.
    In this case, the elevator's target floor should be set to the max floor number.
    """
    moving_algorithm = EndToEndLoop()
    max_floor = 5
    waiting = {1: [], 2: [], 3: [], 4: [], 5: []}  # No people waiting

    elevators = [Elevator(max_floor)]
    moving_algorithm.update_target_floors(elevators, waiting, max_floor)

    assert elevators[0].target_floor == max_floor


###############################################################################
# Sample tests for Part 4
###############################################################################
def test_simple_stats_correct_keys() -> None:
    """Test that the returned statistics dictionary has the correct keys
    for a 5-round simulation.
    """
    config = get_example_config()
    simulation = Simulation(config)
    stats = simulation.run(5)

    actual = sorted(stats.keys())
    expected = ['avg_time', 'max_time', 'num_rounds', 'people_completed', 'total_people']

    assert actual == expected


def test_simple_stats_num_rounds() -> None:
    """Test the returned num_rounds statistic for a 5-round simulation."""
    config = get_example_config()
    simulation = Simulation(config)
    num_rounds = 5
    stats = simulation.run(num_rounds)

    assert stats['num_rounds'] == num_rounds


###############################################################################
# Sample tests for Part 5
###############################################################################
def test_file_arrivals_doctest() -> None:
    """This test performs (essentially) the same check as the FileArrivals doctest we've provided.

    We've included it as a unit test here to make it easier for you to copy this code
    and write your own new test cases!
    """
    my_generator = FileArrivals(5, 'data/sample_arrivals.csv')
    round0_arrivals = my_generator.generate(0)

    assert len(round0_arrivals) == 2
    assert len(round0_arrivals[1]) == 1
    assert len(round0_arrivals[5]) == 1

    floor1_person = round0_arrivals[1][0]
    assert floor1_person.start == 1
    assert floor1_person.target == 4
    assert floor1_person.wait_time == 0

    floor5_person = round0_arrivals[5][0]
    assert floor5_person.start == 5
    assert floor5_person.target == 3
    assert floor5_person.wait_time == 0


def test_furthest_floor_simple() -> None:
    """This test checks the behaviour of the FurthestFloor moving algorithm on a simple example.
    """
    moving_algorithm = FurthestFloor()
    max_floor = 5
    waiting = {1: [], 2: [Person(2, 1)], 3: [], 4: [], 5: [Person(5, 1)]}  # Two people waiting
    elevator = Elevator(max_floor)
    elevator.current_floor = 3
    elevator.target_floor = 3
    moving_algorithm.update_target_floors([elevator], waiting, max_floor)

    assert elevator.target_floor == 5


###############################################################################
# Helpers
###############################################################################
def get_example_config() -> dict:
    """Return an example simulation configuration dictionary.

    Used by several of the provided sample tests. We strongly recommend creating your own
    for additional testing!
    """
    return {
        'num_floors': 6,
        'num_elevators': 2,
        'elevator_capacity': 2,
        'arrival_generator': SingleArrivals(6),
        'moving_algorithm': EndToEndLoop(),
        'visualize': False,  # Note: this is set to False to prevent Pygame from opening a window
    }


if __name__ == '__main__':
    import pytest

    pytest.main(['a1_sample_test.py'])
