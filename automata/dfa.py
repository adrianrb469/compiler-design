from typing import List, Dict
from nfa import State


class DFAState:
    id = 0

    def __init__(self, nfa_states: set[State]):
        self.nfa_states = nfa_states
        self.transitions: Dict[str, "DFAState"] = {}
        self.is_accepting = False
        self.id = DFAState.id
        self.is_start = False
        DFAState.id += 1

    def __str__(self):
        nfa_state_ids = [str(nfa_state.id) for nfa_state in self.nfa_states]
        transitions = ", ".join(
            f"{input} -> {state.id}" for input, state in self.transitions.items()
        )
        return f"DFAState(id={self.id}, is_accepting={self.is_accepting}, is_start={self.is_start}, nfa_states={nfa_state_ids}, transitions={transitions})"


class DFA:
    def __init__(self, initial_state: DFAState, states: List[DFAState]):
        self.initial_state = initial_state
        accepting_states = [state for state in states if state.is_accepting]
        self.final_state = accepting_states[0] if accepting_states else None
        self.states = states

    def input_symbols(self):
        return set(
            transition for state in self.states for transition in state.transitions
        )

    def remove_dead_states(self):
        reachable = set()

        def can_reach_accepting(state, visited=set()):
            if state in reachable:
                return True
            if state in visited:
                return False
            visited.add(state)

            for symbol, next_state in state.transitions.items():
                if next_state.is_accepting or can_reach_accepting(next_state, visited):
                    reachable.add(state)
                    return True
            return False

        # Check reachability from each non-accepting state
        for state in self.states:
            if not state.is_accepting:
                can_reach_accepting(state)

        # Filter out states that cannot reach an accepting state (i.e., dead states)
        self.states = [
            state for state in self.states if state in reachable or state.is_accepting
        ]

        # Update transitions to remove references to removed states
        for state in self.states:
            state.transitions = {
                symbol: next_state
                for symbol, next_state in state.transitions.items()
                if next_state in self.states
            }

    def printme(self):
        for state in self.states:
            for symbol, transition in state.transitions.items():
                print((state.id, transition.id, symbol))

        for state in self.states:
            print(state)

    def run(self, input_string: str, minimized=False):
        state = self.initial_state
        # print(
        #     "Accepting states:",
        #     [state.id for state in self.states if state.is_accepting],
        # )
        [state.id for state in self.states if state.is_accepting]
        for symbol in input_string:
            # print(
            #     "Reading:",
            #     symbol,
            # )
            if symbol not in state.transitions:
                # return "Rejected"
                if not minimized:
                    print(f"DFA simulation with {input_string}: {False}")
                else:
                    print(f"Minimized DFA simulation with {input_string}: {False}")
                return "Rejected"

            # print(
            #     "Current state:",
            #     state.id,
            #     "Next state:",
            #     state.transitions[symbol].id,
            #     "Symbol:",
            #     symbol,
            # )
            state = state.transitions[symbol]

        if not minimized:
            if state.is_accepting:
                print(f"DFA simulation with {input_string}: {True}")
            else:
                print(f"DFA simulation with {input_string}: {False}")
        else:
            if state.is_accepting:
                print(f"Minimized DFA simulation with {input_string}: {True}")
            else:
                print(f"Minimized DFA simulation with {input_string}: {False}")

        return "Rejected"

    def minimize(self):
        # Step 1: Initial partitioning into accepting and non-accepting states
        partitions = {
            frozenset(state for state in self.states if state.is_accepting),
            frozenset(state for state in self.states if not state.is_accepting),
        }

        # Function to find the partition containing a specific state
        def find_partition(state, partitions):
            for partition in partitions:
                if state in partition:
                    return partition
            return None

        # Step 2: Refinement of partitions
        refined = True
        while refined:
            new_partitions = set()
            refined = False
            for partition in partitions:
                # Group states by where their transitions lead for each input symbol
                partition_mapping = {}
                for state in partition:
                    transition_signature = tuple(
                        find_partition(state.transitions.get(symbol), partitions)
                        for symbol in self.input_symbols()
                    )
                    if transition_signature not in partition_mapping:
                        partition_mapping[transition_signature] = set()
                    partition_mapping[transition_signature].add(state)

                if len(partition_mapping) > 1:  # Partition can be refined
                    refined = True
                    new_partitions.update(
                        frozenset(group) for group in partition_mapping.values()
                    )
                else:
                    new_partitions.add(partition)

            partitions = new_partitions

        new_states = []
        partition_to_new_state = {}

        for partition in partitions:
            new_state = DFAState(
                set(partition)
            )  # Initialize with the set of NFA states in the partition
            new_state.is_accepting = any(state.is_accepting for state in partition)
            new_states.append(new_state)
            partition_to_new_state[partition] = new_state

        # Mapping from old DFAState instances to the new DFAState instances
        old_to_new = {}
        for old_state in self.states:
            for partition, new_state in partition_to_new_state.items():
                if old_state in partition:
                    old_to_new[old_state] = new_state
                    break

        # Update transitions for the new DFAState instances
        for new_state in new_states:
            for old_state in new_state.nfa_states:
                for input_symbol, target_state in old_state.transitions.items():
                    # Map the target_state to its corresponding new DFAState
                    if (
                        target_state in old_to_new
                    ):  # Ensure target_state is in the mapping
                        new_target_state = old_to_new[target_state]
                        new_state.transitions[input_symbol] = new_target_state

        # Identify the new initial state and update it as the start state
        for old_state, new_state in old_to_new.items():
            if old_state.is_start:
                new_initial = new_state
                new_initial.is_start = True
                break

        # Update the DFA with the new structure
        self.initial_state = new_initial
        self.states = set(new_states)  # Assuming states are now stored in a set
