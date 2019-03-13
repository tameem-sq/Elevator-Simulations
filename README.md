# Elevator Simulations

To run the program, run the python file simulation.py and a pygame window will appear.

Refer to the .png file in this repository to see what the pygame window will look like.

![Screenshot](Elevator-Simulations/sample simulation screenshot.png)

To run this program, you will need python 3.0 or grater, and pygame installed.

Elevator moving algorithms
Each round, an elevator moving algorithm makes a decision about where each elevator should move.
Because an elevator can only move one floor per round, this decision can have one of three outputs: the
elevator should move up, move down, or stay in the same location.
A moving algorithm receives as input two values: a list of all the elevators in the simulation, and a
dictionary mapping floor numbers to a list of people who are waiting on that floor. It outputs a list of
decisions (one for each elevator) specifying in which direction it should move.
This is an extremely flexible model of how elevators move (in real-life, the use of elevator buttons makes
this much more constrained), and the reason this was done is so that a variety of
fun and interesting elevator algorithms could be implemented! This program implements the following three
algorithms.

Random algorithm
The algorithm makes a random decision for each elevator, choosing between each of the three
possibilities with equal probability. These choices are made independently for each elevator.

Pushy Passenger algorithm
This algorithm makes a decision independently for each elevator.
If the elevator is empty (has no passengers), it moves towards thelowest floor that has at least one
person waiting, or stays still if there are no people waiting. Because the decisions are independent for
each elevator, if at least one person is waiting, all empty elevators move to the same floor.
If the elevator isn’t empty, it moves towards the target floor of thefirst passenger who boarded the
elevator.

Short-sighted algorithm
This algorithm makes a decision independently for each elevator.
If the elevator is empty, it moves towards theclosest floor that has at least one person waiting, or stays
still if there are no people waiting. In the case of ties (e.g. if the elevator is at floor 3, and there are
people waiting at floors 2 and 4), it moves towards the lower floor. As in the previous algorithm, because
the decisions are independent for each elevator, all empty elevators move to the same floor.(Updated,
the previous sentence didn’t make sense for this algorithm, and should be ignored.)
If the elevator isn’t empty, it moves towards the closest target floor of all passengers who are on the
elevator, again breaking ties by moving towards the lower floor. In this case, the order in which people
boarded does not matter.
