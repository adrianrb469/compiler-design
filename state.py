from typing import List


class Transition:
    def __init__(self, input: str, state):
        self.input = input
        self.state = state


class State:
    instance = 0

    def __init__(self, transitions: List[Transition] = None):
        self.transitions = []
        self.symbol = self.instance
        self.instance += 1
        if transitions:
            self.transitions = transitions

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def epsilon_closure(self):
        closure = {self}
        states_to_process = [self]

        while states_to_process:
            current_state = states_to_process.pop()
            for transition in current_state.transitions:
                if transition.input is None and transition.new_state not in closure:
                    closure.add(transition.new_state)
                    states_to_process.append(transition.new_state)

        return closure
