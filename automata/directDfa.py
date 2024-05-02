from automata.render import create_direct_dfa_graph

R_END = "※"


class DirectDFAState:
    def __init__(
        self,
        state,
        state_id,
        marked=False,
        accepting=False,
        initial=False,
        accept_pos=None,
        subset=set(),
    ):
        self.state = state
        self.accepting = accepting
        self.marked = marked
        self.initial = initial
        self.subset = subset
        self.state_id = state_id
        self.transitions = {}
        self.transitions_ids = {}
        self.accept_pos = accept_pos
        self.action = None
        self.label = None


class DirectDFA:
    def __init__(self):
        self.states = []
        self.initial_state = None
        self.final_states = set()
        self.state_counter = 0

    def generate_direct_dfa(self, syntax_tree, root):
        followPosTable, posTable = syntax_tree.followPosTable, syntax_tree.posTable

        initial_state = DirectDFAState(
            state=root.firstPos,
            state_id=self.state_counter,
            initial=True,
            subset=root.firstPos,
        )
        self.initial_state, self.states, self.state_counter = (
            initial_state,
            [initial_state],
            self.state_counter + 1,
        )

        for pos in initial_state.state:
            if pos in posTable[R_END]:
                initial_state.accepting, initial_state.accept_pos = True, pos
                self.final_states.add(initial_state)

        alphabet = syntax_tree.operands

        counter, new_states, first_iteration = 0, 0, False

        while counter != new_states or not first_iteration:

            first_iteration, counter = True, counter + (new_states != 0)

            for symbol in alphabet:
                change = True
                subset = set()

                for pos in self.states[counter].state:
                    if pos in posTable[symbol]:
                        subset = subset.union(followPosTable[pos])

                # Check if the new state is already created
                for state in self.states:
                    if state.state == subset:
                        self.states[counter].transitions[symbol] = state

                        self.states[counter].transitions_ids[symbol] = state.state_id

                        change = False
                        break

                if change and len(subset) > 0:
                    new_state = DirectDFAState(
                        state=subset, subset=subset, state_id=self.state_counter
                    )
                    self.states[counter].transitions_ids[symbol] = self.state_counter

                    self.state_counter += 1

                    for pos in new_state.state:
                        if pos in posTable[R_END]:
                            new_state.accepting = True
                            new_state.accept_pos = pos
                            self.final_states.add(new_state)
                            break

                    self.states[counter].transitions[symbol] = new_state

                    self.states.append(new_state)
                    new_states += 1

        return self

    def get_state(self, positions):
        for state in self.states:
            if state.state == positions:
                return state
        new_state = DirectDFAState(positions)
        return new_state

    def set_actions(self, rule_tokens):
        acceptance_positions = [
            state.accept_pos for state in self.states if state.accepting
        ]
        sorted_acceptance_positions = sorted(list(set(acceptance_positions)))

        for state in self.states:
            if state.accept_pos is not None:
                token, action = rule_tokens[
                    sorted_acceptance_positions.index(state.accept_pos)
                ]
                state.action = action
                state.label = token

    def render(self):
        create_direct_dfa_graph(self, False)

    def minimize(self):
        # Step 1: Remove unreachable states
        reachable_states = self.get_reachable_states()
        self.states = [state for state in self.states if state in reachable_states]

        # Step 2: Mark all states as unmarked
        for state in self.states:
            state.marked = False

        # Step 3: Mark all accepting states
        for state in self.states:
            if state.accepting:
                state.marked = True

        # Step 4: Mark all states that have transitions to marked states
        marked_states = [state for state in self.states if state.marked]

        while True:
            for state in self.states:
                if state not in marked_states:
                    for symbol, next_state in state.transitions.items():
                        if next_state in marked_states:
                            state.marked = True
                            marked_states.append(state)
                            break
            if len(marked_states) == len(self.states):
                break

        # Step 5: Split the states into two groups: marked and unmarked
        marked_states = [state for state in self.states if state.marked]
        unmarked_states = [state for state in self.states if not state.marked]

        # Step 6: Repeat until no more states can be split

        while True:
            split = False
            for state in self.states:
                if state not in marked_states and state not in unmarked_states:
                    for marked_state in marked_states:
                        if self.can_split(
                            state, marked_state, marked_states, unmarked_states
                        ):
                            split = True
                            break
                    if split:
                        break
            if not split:
                break

        # Step 7: Combine the states
        new_states = []
        for state in marked_states:
            new_state = DirectDFAState(
                state.state,
                marked=state.marked,
                accepting=state.accepting,
                initial=state.initial,
                accept_pos=state.accept_pos,
            )
            new_state.action = state.action
            new_state.label = state.label
            new_states.append(new_state)

        for state in unmarked_states:
            new_state = DirectDFAState(
                state.state,
                marked=state.marked,
                accepting=state.accepting,
                initial=state.initial,
                accept_pos=state.accept_pos,
            )
            new_state.action = state.action
            new_state.label = state.label
            new_states.append(new_state)

        self.states = new_states

        # Step 8: Update the transitions
        for state in self.states:
            for symbol, next_state in state.transitions.items():
                state.transitions[symbol] = self.get_new_state(
                    next_state, marked_states, unmarked_states
                )

        # Step 9: Update the initial state
        self.initial_state = self.get_new_state(
            self.initial_state, marked_states, unmarked_states
        )

        # Step 10: Update the final states
        self.final_states = set(
            [
                self.get_new_state(state, marked_states, unmarked_states)
                for state in self.final_states
            ]
        )

    def can_split(self, state, marked_state, marked_states, unmarked_states):
        for symbol, next_state in state.transitions.items():
            if next_state in marked_states:
                return True
        return False

    def get_new_state(self, old_state, marked_states, unmarked_states):
        for state in marked_states + unmarked_states:
            if state.state == old_state.state:
                return state
        return None

    def get_reachable_states(self):
        reachable_states = set()
        stack = [self.initial_state]
        while stack:
            current_state = stack.pop()
            reachable_states.add(current_state)
            for symbol, next_state in current_state.transitions.items():
                if next_state not in reachable_states:
                    stack.append(next_state)
        return reachable_states
