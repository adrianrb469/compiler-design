from utils import shunting_yard
from nfa import NFA, State, Transition


def regex_to_nfa(regex: str) -> NFA:
    nfa_stack = []
    expression = shunting_yard(regex)

    for token in expression:
        if token.isalnum() or token == "ϵ":
            state1, state2 = State(), State()
            state1.add_transition(Transition(token, state2))
            nfa_stack.append(NFA(state1, state2))
        elif token == "*":
            nfa = nfa_stack.pop()
            state1, state2 = State(), State()
            state1.add_transition(Transition("ϵ", nfa.initial_state))
            state1.add_transition(Transition("ϵ", state2))
            nfa.final_state.add_transition(Transition("ϵ", nfa.initial_state))
            nfa.final_state.add_transition(Transition("ϵ", state2))
            nfa_stack.append(NFA(state1, state2))
        elif token == "|":
            nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
            state1, state2 = State(), State()
            state1.add_transition(Transition("ϵ", nfa1.initial_state))
            state1.add_transition(Transition("ϵ", nfa2.initial_state))
            nfa1.final_state.add_transition(Transition("ϵ", state2))
            nfa2.final_state.add_transition(Transition("ϵ", state2))
            nfa_stack.append(NFA(state1, state2))
        elif token == ".":
            nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
            nfa1.final_state.add_transition(Transition("ϵ", nfa2.initial_state))
            nfa_stack.append(NFA(nfa1.initial_state, nfa2.final_state))
        elif token == "+":
            nfa = nfa_stack.pop()
            state1, state2 = State(), State()
            state1.add_transition(Transition("ϵ", nfa.initial_state))
            nfa.final_state.add_transition(Transition("ϵ", nfa.initial_state))
            nfa.final_state.add_transition(Transition("ϵ", state2))
            nfa_stack.append(NFA(state1, state2))
        elif token == "?":
            nfa = nfa_stack.pop()
            state1, state2 = State(), State()
            state1.add_transition(Transition("ϵ", nfa.initial_state))
            state1.add_transition(Transition("ϵ", state2))
            nfa.final_state.add_transition(Transition("ϵ", state2))
            nfa_stack.append(NFA(state1, state2))

    final_nfa = nfa_stack.pop()
    final_nfa.final_state.is_accepting = True

    return final_nfa


def get_all_states(initial_state: State, visited: set[State] = None) -> set[State]:
    if visited is None:
        visited = set()
    visited.add(initial_state)
    for transition in initial_state.transitions:
        if transition.new_state not in visited:
            get_all_states(transition.new_state, visited)
    return visited
