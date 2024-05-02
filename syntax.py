import pydotplus

from Yapar import Yapar


def closure(I):
    J = []
    J.extend(I)
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


def construct_lr0_automata(grammar):

    states = []
    transitions = {}

    # Aumentamos la gramtica, con S' -> S
    S = grammar["P"][0][0]
    augmented_production = [S + "'", [S]]
    grammar["P"].insert(0, augmented_production)
    grammar["NT"].insert(0, S + "'")

    print("Terminals:")
    print(grammar["T"])
    print("Non-terminals:")
    print(grammar["NT"])
    print("Productions:")
    for production in grammar["P"]:
        print(f"  {production[0]} -> {' '.join(production[1])}")

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

        for item in current_state:
            if item not in kernel_items:
                print(f"  {item[0]} -> {''.join(item[1])}")

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

    # Visualizacion
    dot = pydotplus.Dot(graph_type="digraph")
    dot.set_rankdir("TB")
    dot.set_size('"8,5"')

    kernel_color = "#ffffff"

    for i, state in enumerate(states):
        state_label = f"S{i}:\n"

        kernel_items = [item for item in state if item[1][0] != "." or item == state[0]]

        is_accepting = False
        for item in kernel_items:
            if item[0] == grammar["P"][0][0] and "." == item[1][-1]:
                is_accepting = True
                break

        state_label += "Kernel items:\n"
        for item in kernel_items:
            state_label += f"  {item[0]} -> {' '.join(item[1])}\n"

        state_label += "\nClosure items:\n"
        for item in state:
            if item not in kernel_items:
                state_label += f"  {item[0]} -> {' '.join(item[1])}\n"

        node = pydotplus.Node(
            str(i),
            label=state_label,
            shape="rectangle",
            style="filled",
            fontsize="10",
            fillcolor=kernel_color,
        )
        dot.add_node(node)

    for from_state, transition in transitions.items():
        for symbol, to_state in transition.items():
            if symbol == "$" and to_state == "Accept":
                accept_node = pydotplus.Node(
                    "Accept", label="Accept", shape="plaintext"
                )
                dot.add_node(accept_node)
                edge = pydotplus.Edge(
                    str(from_state), "Accept", label="$", arrowhead="normal"
                )
            else:
                edge = pydotplus.Edge(str(from_state), str(to_state), label=symbol)
            dot.add_edge(edge)

    return dot


yapar = Yapar("slr1.yalp")
yapar.parse()
grammar = yapar.get_grammar()

lr0_automata = construct_lr0_automata(grammar)

with open("lr0_automata.dot", "w") as file:
    file.write(lr0_automata.to_string())

lr0_automata.write_pdf("lr0_automata.pdf")
