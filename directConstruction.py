from syntax_tree import *
from render import create_direct_dfa_graph


class DirectDFAState:
    def __init__(self, state, marked=False, accepting=False, initial=False):
        self.state = state
        self.accepting = accepting
        self.marked = marked
        self.initial = initial


class DirectDFATransition:
    def __init__(self, symbol, originState, destinationState):
        self.symbol = symbol
        self.originState = originState
        self.destinationState = destinationState


class DirectDFA:
    def __init__(self, tree):
        self.states, self.transitions, self.alphabet = self.directConstruction(tree)
        self.tree = tree

    def step(self, current_state, input_symbol):
        for transition in self.transitions:
            if (
                transition.originState == current_state
                and transition.symbol == input_symbol
            ):
                return transition.destinationState
        return None  # return None if no valid transition exists

    def directConstruction(self, tree):
        # regex = "(" + regex + ")#"
        Dstates = []
        Dtransitions = []
        # tree = SyntaxTree(regex)
        language = tree.operands
        node_map = tree.render()
        Dstates.append(
            DirectDFAState(calc_firstpos(tree.root), False, False, True)
        )  # store root first pos

        nodeValueAndFollowpos = []
        for (
            k,
            v,
        ) in (
            node_map.items()
        ):  # store node id, value, and followpos for every leaf node
            nodeSet = v.followpos
            if nodeSet == set():
                nodeSet = {"Ø"}
            nodeValueAndFollowpos.append([k, v.value, nodeSet])

        # for node in nodeValueAndFollowpos: # for every node in nodeValueAndFollowpos
        #     print(f'Node: {node[0]}, Value: {node[1]}, Followpos: {node[2]}')

        statesCounter = 0
        currentState = Dstates[
            statesCounter
        ]  # set current state to the first state in Dstates before entering while

        while any(
            not state.marked for state in Dstates
        ):  # if are any unmarked (False) state in Dstates
            currentState.marked = True  # mark current state as marked (True)
            for symbol in language:  # for every symbol in the operands of the regex
                newState = set()  # create a new set for the new state
                for (
                    node
                ) in currentState.state:  # for every follow pos in the current state
                    if isinstance(node, int):  # if the node is a digit
                        if (
                            symbol == nodeValueAndFollowpos[node - 1][1]
                        ):  # if the symbol matches the value of the node
                            newState = newState.union(
                                nodeValueAndFollowpos[node - 1][2]
                            )  # add the follow pos of the node to the new state
                    else:
                        newState = {
                            "Ø"
                        }  # if the node is not a digit, set the new state to empty
                if not newState == set():  # if the new state is not empty
                    currentStates = []  # create a new list for just the current states sets
                    for state in Dstates:  # for every state in Dstates
                        currentStates.append(
                            state.state
                        )  # add each state set() to the list to have all states and do a easy .contains() method check
                    # if len(currentStates) > 0:
                    if (newState is not None) and not (
                        newState in currentStates
                    ):  # if the new state is not in the list of current states
                        acceptingState = False
                        for endNode in newState:
                            if isinstance(endNode, int):
                                if nodeValueAndFollowpos[endNode - 1][2] == {"Ø"}:
                                    acceptingState = True
                                    break
                        Dstates.append(
                            DirectDFAState(newState, False, acceptingState)
                        )  # add the new state to Dstates
                    if currentState.state != {"Ø"}:  # if the current state is not empty
                        Dtransitions.append(
                            DirectDFATransition(symbol, currentState.state, newState)
                        )  # add the transition to Dtransitions
            statesCounter += 1  # increment the counter
            if statesCounter < len(Dstates):
                currentState = Dstates[statesCounter]

        return Dstates, Dtransitions, language

    def render(self, minimized=False):
        create_direct_dfa_graph(self.states, self.transitions, minimized)

    def run(self, string, minimized=False):
        # Verify if the string has chars that are not in the alphabet
        for char in string:
            if char not in self.alphabet:
                if not minimized:
                    print(f"Direct DFA simulation: {False}")
                else:
                    print(f"Minimized Direct DFA simulation: {False}")
                return False
        if string[-1] != "#":
            string += "#"

        currentState = self.states[0]
        for char in string:
            transitionFound = False
            for transition in self.transitions:
                # print(currentState.state,transition.originState,transition.symbol,'-',char,transition.destinationState)
                if (
                    set(transition.originState) == set(currentState.state)
                    and transition.symbol == char
                    and char != "#"
                ):
                    for state in self.states:
                        if state.state == transition.destinationState:
                            currentState = state
                            transitionFound = True
                            # print('\tEureka!', char, currentState.state)
                            break
                    break
            if not transitionFound and char != "#":
                if not minimized:
                    print(f"Direct DFA simulation: {False}")
                else:
                    print(f"Minimized Direct DFA simulation: {False}")
                return False
        # for transition in self.transitions:
        #     print(transition.symbol, transition.originState, transition.destinationState)
        # for state in self.states:
        #     print(state.state, state.accepting)
        if currentState.accepting:
            if not minimized:
                print(f"Direct DFA simulation: {True}")
            else:
                print(f"Minimized Direct DFA simulation: {True}")
            return True
        else:
            if not minimized:
                print(f"Direct DFA simulation: {False}")
            else:
                print(f"Minimized Direct DFA simulation: {False}")
            return False

    def minimize(self):
        # Step 1: Initialize partitions
        accepting_states = set()
        non_accepting_states = set()
        for state in self.states:
            if state.accepting:
                accepting_states.add(state)
            else:
                non_accepting_states.add(state)

        partitions = [accepting_states, non_accepting_states]

        # Step 2: Refine partitions until no change occurs
        while True:
            new_partitions = []
            for partition in partitions:
                for symbol in self.alphabet:
                    # Split the partition based on transitions
                    split_partition = self.split_partition(
                        partition, symbol, partitions
                    )
                    if split_partition:
                        new_partitions.extend(split_partition)

            if new_partitions == partitions:
                break
            partitions = new_partitions

        # Step 3: Create new states and transitions
        new_states = []
        new_transitions = []

        for i, partition in enumerate(partitions):
            new_state = DirectDFAState(
                partition,
                initial=(i == 0),
                accepting=(True in {state.accepting for state in partition}),
            )
            new_states.append(new_state)

        for transition in self.transitions:
            origin_partition = self.find_partition(transition.originState, partitions)
            destination_partition = self.find_partition(
                transition.destinationState, partitions
            )

            if origin_partition != destination_partition:
                # Create a new transition between the representative states of the partitions
                new_transition = DirectDFATransition(
                    transition.symbol,
                    new_states[partitions.index(origin_partition)],
                    new_states[partitions.index(destination_partition)],
                )
                new_transitions.append(new_transition)

        # Update the DirectDFA instance with minimized states and transitions
        # self.states = new_states
        # self.transitions = new_transitions

    def split_partition(self, partition, symbol, partitions):
        # Helper method to split a partition based on transitions with a given symbol
        result = []

        if symbol == "#":
            return [partition]

        for state in partition:
            transition_found = False

            for other_partition in partitions:
                for other_state in other_partition:
                    if state != set() and other_state != set():
                        # Find the transition corresponding to the current symbol
                        # origin_transitions = [t for t in self.transitions if set(t.originState) == set(state.state) and t.symbol == symbol]
                        # destination_transitions = [t for t in self.transitions if set(t.originState) == set(other_state.state) and t.symbol == symbol]

                        # if origin_transitions and destination_transitions and set(origin_transitions[0].destinationState) != set(destination_transitions[0].destinationState):
                        # Split the partition if the transitions lead to different states
                        # result.append({state} for state in partition)
                        transition_found = True
                        break

            if transition_found:
                break

            if not transition_found:
                result.append(partition)

        return result

    def find_partition(self, state_set, partitions):
        # Helper method to find the partition containing a given state set
        for partition in partitions:
            if state_set in partition:
                return partition
        return None
