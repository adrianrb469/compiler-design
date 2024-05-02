import pydotplus

from Yalex import Yalex
from Yapar import Yapar


def main():

    yalex = Yalex("examples/slr-1.yal", debug=False)

    lex_tokens = []

    for key, value in yalex.tokens:
        if key == "":
            continue
        lex_tokens.append(key)

    print("Tokens in lexer:")
    print(lex_tokens, "\n")

    yapar = Yapar("slr1.yalp")
    yapar.parse()
    grammar = yapar.get_grammar()

    for terminal in grammar["T"]:
        if terminal not in lex_tokens:
            raise Exception(f"Terminal {terminal} not in lexer tokens")

    print("Grammar:")
    print("Terminals:")
    print(grammar["T"], "\n")
    print("Non-terminals:")
    print(grammar["NT"], "\n")

    print("Productions:")
    for production in grammar["P"]:
        print(f"  {production[0]} -> {' '.join(production[1])}")
    print("\n")

    print("LR0 saved in lr0_automata.pdf")

    lr0_automata = construct_lr0_automata(grammar)


def visualize_lr0_automaton(states, transitions, grammar, kernel_color="lightblue"):
    dot = pydotplus.Dot(
        graph_type="digraph", rankdir="TB", fontname="SF Mono", fontsize="10"
    )

    for i, state in enumerate(states):
        state_label = f"<\n<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>\n"
        state_label += f"<TR><TD COLSPAN='2'><B>I{i}</B></TD></TR>\n"

        kernel_items = [item for item in state if item[1][0] != "." or item == state[0]]
        is_accepting = False
        for item in kernel_items:
            if item[0] == grammar["P"][0][0] and "." == item[1][-1]:
                is_accepting = True
                break

        state_label += "<TR><TD COLSPAN='2'><B>Kernel items:</B></TD></TR>\n"
        for item in kernel_items:
            state_label += f"<TR><TD>{item[0]}</TD><TD>{' '.join(item[1])}</TD></TR>\n"

        state_label += "<TR><TD COLSPAN='2'><B>Closure items:</B></TD></TR>\n"
        for item in state:
            if item not in kernel_items:
                state_label += (
                    f"<TR><TD>{item[0]}</TD><TD>{' '.join(item[1])}</TD></TR>\n"
                )

        state_label += "</TABLE>\n>"

        node = pydotplus.Node(
            str(i),
            label=state_label,
            shape="plaintext",
            fontname="CMU Serif",
            fontsize="12",
        )

        dot.add_node(node)

    for from_state, transition in transitions.items():
        for symbol, to_state in transition.items():
            if symbol == "$" and to_state == "Accept":
                accept_node = pydotplus.Node(
                    "Accept",
                    label="Accept",
                    shape="plaintext",
                    fontname="CMU Serif Bold",
                    fontsize="14",
                )
                dot.add_node(accept_node)
                edge = pydotplus.Edge(
                    str(from_state),
                    "Accept",
                    label="$",
                    arrowhead="normal",
                    fontname="CMU Serif",
                    fontsize="14",
                )
            else:

                edge = pydotplus.Edge(
                    str(from_state),
                    str(to_state),
                    label=symbol,
                    fontname="CMU Serif",
                    fontsize="14",
                )
            dot.add_edge(edge)

    return dot


def construct_lr0_automata(grammar: dict):

    # items, son todos los simbolos de la gramatica (terminales y no terminales)
    def closure(items):
        J = []
        J.extend(items)
        added = True
        while added:
            added = False
            for item in J:
                if "." in item[1] and item[1].index(".") != len(item[1]) - 1:
                    next_symbol = item[1][item[1].index(".") + 1]
                    if next_symbol in grammar["NT"]:
                        for production in grammar["P"]:
                            if production[0] == next_symbol:
                                new_item = [production[0], production[1].copy()]
                                new_item[1].insert(0, ".")
                                if new_item not in J:
                                    J.append(new_item)
                                    added = True
        return J

    def goto(items, symbol):
        goto_items = []
        for item in items:
            if "." in item[1]:
                dot_pos = item[1].index(".")
                if dot_pos < len(item[1]) - 1:
                    next_symbol = item[1][dot_pos + 1]
                    if next_symbol == symbol:
                        new_item = [
                            item[0],
                            item[1][:dot_pos]
                            + [item[1][dot_pos + 1], "."]
                            + item[1][dot_pos + 2 :],
                        ]
                        goto_items.append(new_item)
        return closure(goto_items)

    states = []
    transitions = {}

    # Aumentamos la gramtica, con S' -> S
    S = grammar["P"][0][0]
    augmented_production = [S + "'", [S]]
    grammar["P"].insert(0, augmented_production)
    grammar["NT"].insert(0, S + "'")

    # El estado inicial es closure({S' -> .S})
    first = [grammar["P"][0][0], grammar["P"][0][1].copy()]
    first[1].insert(0, ".")
    initial_state = closure([first])
    states.append(initial_state)

    state_queue = [initial_state]
    while state_queue:
        current_state = state_queue.pop(0)
        kernel_items = [
            item
            for item in current_state
            if item[1][0] != "." or item == current_state[0]
        ]

        accept_item = None

        # El estado es de aceptacion si contiene una produccion de la forma S' -> S. (con el punto al final)
        for item in kernel_items:
            if item[0] == grammar["P"][0][0] and "." == item[1][-1]:
                accept_item = item

        current_state_index = states.index(current_state)
        if accept_item is not None:
            if current_state_index not in transitions:
                transitions[current_state_index] = {}
            transitions[current_state_index]["$"] = "Accept"

        for symbol in grammar["items"]:
            next_state = goto(
                current_state, symbol
            )  # Calculamos el siguiente estado, dado el simbolo
            if next_state and next_state not in states:
                states.append(next_state)
                state_queue.append(next_state)
            if next_state:
                next_state_index = states.index(next_state)
                if current_state_index not in transitions:
                    transitions[current_state_index] = {}
                transitions[current_state_index][symbol] = next_state_index

    visual = visualize_lr0_automaton(states, transitions, grammar)
    visual.write_pdf("lr0_automata.pdf")


if __name__ == "__main__":
    main()
