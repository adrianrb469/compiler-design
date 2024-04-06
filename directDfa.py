from render import create_direct_dfa_graph

class DirectDFAState:
    def __init__(self, state, marked=False, accepting=False, initial=False, accept_pos=None):
        self.state = state
        self.accepting = accepting
        self.marked = marked
        self.initial = initial
        self.transitions = {}  # Transitions from the state
        self.accept_pos = accept_pos  # Position of '#' if it exists in the state
        self.action = None  # Action associated with the state
        self.label = None  # Label associated with the state

class DirectDFA:
    def __init__(self):
        self.states = []
        self.initial_state = None
        self.final_states = set()

    def generate_direct_dfa(self, syntax_tree):
        initial_positions = syntax_tree.root.firstpos
        self.initial_state = self.get_state(initial_positions)
        self.initial_state.initial = True
        self.states.append(self.initial_state)

        queue = [self.initial_state]
        while queue:
            current_state = queue.pop(0)
            for symbol in syntax_tree.operands:
                next_positions = set()
                for position in current_state.state:
                    if syntax_tree.node_map[position].value == symbol:
                        next_positions.update(syntax_tree.node_map[position].followpos)
                if next_positions:
                    next_state = self.get_state(next_positions)
                    current_state.transitions[symbol] = next_state
                    if next_state not in self.states:
                        self.states.append(next_state)
                        queue.append(next_state)
                    if any(syntax_tree.node_map[pos].value == '#' for pos in next_positions):
                        next_state.accepting = True
                        next_state.accept_pos = next(pos for pos in next_positions if syntax_tree.node_map[pos].value == '#')
                        self.final_states.add(next_state)

    def get_state(self, positions):
        for state in self.states:
            if state.state == positions:
                return state
        new_state = DirectDFAState(positions)
        return new_state

    def set_actions(self, rule_tokens):
        acceptance_positions = [state.accept_pos for state in self.states if state.accept_pos is not None]
        sorted_acceptance_positions = sorted(list(set(acceptance_positions))) # we sort them, as they are the same as the order of the tokens
        for state in self.states:
            if state.accept_pos is not None:
                token, action = rule_tokens[sorted_acceptance_positions.index(state.accept_pos)] # directly get the token and action from the index
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
                        if self.can_split(state, marked_state, marked_states, unmarked_states):
                            split = True
                            break
                    if split:
                        break
            if not split:
                break
            
        # Step 7: Combine the states
        new_states = []
        for state in marked_states:
            new_state = DirectDFAState(state.state, marked=state.marked, accepting=state.accepting, initial=state.initial, accept_pos=state.accept_pos)
            new_state.action = state.action
            new_state.label = state.label
            new_states.append(new_state)
        
        for state in unmarked_states:
            new_state = DirectDFAState(state.state, marked=state.marked, accepting=state.accepting, initial=state.initial, accept_pos=state.accept_pos)
            new_state.action = state.action
            new_state.label = state.label
            new_states.append(new_state)
            
        self.states = new_states
        
        # Step 8: Update the transitions
        for state in self.states:
            for symbol, next_state in state.transitions.items():
                state.transitions[symbol] = self.get_new_state(next_state, marked_states, unmarked_states)
                
        # Step 9: Update the initial state
        self.initial_state = self.get_new_state(self.initial_state, marked_states, unmarked_states)
        
        # Step 10: Update the final states
        self.final_states = set([self.get_new_state(state, marked_states, unmarked_states) for state in self.final_states])
        
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
