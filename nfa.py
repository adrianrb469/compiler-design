from typing import List


class Transition:
    def __init__(self, input, new_state):
        self.input = input
        self.new_state = new_state


class State:
    count = 0

    def __init__(self, transitions: List[Transition] = None):
        self.transitions = []
        self.id = State.count
        self.is_accepting = False
        State.count += 1

        if transitions:
            self.transitions = transitions

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def epsilon_closure(self):
        closure = {self}
        stack = [self]
        while stack:
            current_state = stack.pop()
            for transition in current_state.transitions:
                if transition.input == "ϵ" and transition.new_state not in closure:
                    closure.add(transition.new_state)
                    stack.append(transition.new_state)
        return closure


class NFA:
    def __init__(self, initial_state: State, final_state: State):
        self.initial_state = initial_state
        self.final_state = final_state
        self.states = self.get_all_states(initial_state)

    def get_all_states(
        self, initial_state: State, visited: set[State] = None
    ) -> set[State]:
        if visited is None:
            visited = set()
        visited.add(initial_state)
        for transition in initial_state.transitions:
            if transition.new_state not in visited:
                self.get_all_states(transition.new_state, visited)
        return visited

    def input_symbols(self):
        return set(
            transition.input
            for state in self.states
            for transition in state.transitions
            if transition.input != "ϵ"  # Exclude epsilon transitions
        )

    def run(self, input_string: str) -> bool:
        current_states = self.initial_state.epsilon_closure()

        # print(f"Initial states: {[state.id for state in current_states]}")
        # print(
        #     f"Accepting states: {[state.id for state in self.states if state.is_accepting]}"
        # )

        for character in input_string:
            # print set of current states ids
            # print(f"Current states: {[state.id for state in current_states]}")
            # print(f"Reading: {character}")

            next_states = set()
            for state in current_states:
                for transition in state.transitions:
                    if transition.input == character:
                        next_states = next_states.union(
                            transition.new_state.epsilon_closure()
                        )
            current_states = next_states

        # Check if any of the current states is an accepting state
        # if any(state.is_accepting for state in current_states):
        #     return "Accepted"
        
        if any(state.is_accepting for state in current_states):
            print(f'NFA simulation: {True}')
        else:
            print(f'NFA simulation: {False}')

        return "Rejected"
