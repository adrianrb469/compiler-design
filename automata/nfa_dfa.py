from dfa import DFA, DFAState
from nfa import NFA


def nfa_to_dfa(nfa: NFA):
    initial_dfa_state = DFAState(nfa.initial_state.epsilon_closure())
    initial_dfa_state.is_accepting = any(
        state.is_accepting for state in initial_dfa_state.nfa_states
    )

    dfa_states = {frozenset(initial_dfa_state.nfa_states): initial_dfa_state}
    queue = [initial_dfa_state]
    input_symbols = nfa.input_symbols()

    while queue:
        current_dfa_state = queue.pop(0)

        # For each input symbol, create new DFA states from reachable NFA states
        for symbol in input_symbols:
            new_nfa_states = set()
            for nfa_state in current_dfa_state.nfa_states:
                for transition in nfa_state.transitions:
                    if transition.input == symbol:
                        new_nfa_states |= transition.new_state.epsilon_closure()

            new_nfa_states_frozenset = frozenset(new_nfa_states)
            if new_nfa_states_frozenset not in dfa_states:
                new_dfa_state = DFAState(new_nfa_states)
                new_dfa_state.is_accepting = any(
                    state.is_accepting for state in new_dfa_state.nfa_states
                )
                # Skip dead states
                if not new_dfa_state.is_accepting and not any(
                    state.transitions for state in new_dfa_state.nfa_states
                ):
                    continue
                dfa_states[new_nfa_states_frozenset] = new_dfa_state
                queue.append(new_dfa_state)

            current_dfa_state.transitions[symbol] = dfa_states[new_nfa_states_frozenset]

    initial_dfa_state.is_start = True
    return DFA(initial_dfa_state, list(dfa_states.values()))
