import pydotplus
from tabulate import tabulate


class LR0:
    """
    LR(0) parser generator, based on the grammar provided.

    """

    def __init__(self, grammar: dict):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.build()

    def closure(self, items):
        J = []
        J.extend(items)
        added = True
        while added:
            added = False
            for item in J:
                if "." in item[1] and item[1].index(".") != len(item[1]) - 1:
                    next_symbol = item[1][item[1].index(".") + 1]
                    if next_symbol in self.grammar["NT"]:
                        for production in self.grammar["P"]:
                            if production[0] == next_symbol:
                                new_item = [production[0], production[1].copy()]
                                new_item[1].insert(0, ".")
                                if new_item not in J:
                                    J.append(new_item)
                                    added = True
        return J

    def goto(self, items, symbol):
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
        return self.closure(goto_items)

    def build(self):
        # S' -> S
        S = self.grammar["P"][0][0]
        augmented_production = [S + "'", [S]]
        self.grammar["P"].insert(0, augmented_production)
        self.grammar["NT"].insert(0, S + "'")

        # closure({S' -> .S})
        first = [self.grammar["P"][0][0], self.grammar["P"][0][1].copy()]
        first[1].insert(0, ".")
        initial_state = self.closure([first])
        self.states.append(initial_state)

        state_queue = [initial_state]
        while state_queue:
            current_state = state_queue.pop(0)
            kernel_items = [
                item
                for item in current_state
                if item[1][0] != "." or item == current_state[0]
            ]

            accept_item = None

            for item in kernel_items:
                if item[0] == self.grammar["P"][0][0] and "." == item[1][-1]:
                    accept_item = item

            current_state_index = self.states.index(current_state)
            if accept_item is not None:
                if current_state_index not in self.transitions:
                    self.transitions[current_state_index] = {}
                self.transitions[current_state_index]["$"] = "Accept"

            for symbol in self.grammar["items"]:
                next_state = self.goto(current_state, symbol)
                if next_state and next_state not in self.states:
                    self.states.append(next_state)
                    state_queue.append(next_state)
                if next_state:
                    next_state_index = self.states.index(next_state)
                    if current_state_index not in self.transitions:
                        self.transitions[current_state_index] = {}
                    self.transitions[current_state_index][symbol] = next_state_index

    def visualize(self):
        dot = pydotplus.Dot(
            graph_type="digraph", rankdir="TB", fontname="SF Mono", fontsize="10"
        )

        for i, state in enumerate(self.states):
            state_label = f"<\n<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>\n"
            state_label += f"<TR><TD COLSPAN='2'><B>I{i}</B></TD></TR>\n"

            kernel_items = [
                item for item in state if item[1][0] != "." or item == state[0]
            ]

            state_label += "<TR><TD COLSPAN='2'><B>Kernel items:</B></TD></TR>\n"
            for item in kernel_items:
                state_label += (
                    f"<TR><TD>{item[0]}</TD><TD>{' '.join(item[1])}</TD></TR>\n"
                )

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

        for from_state, transition in self.transitions.items():
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

    def parsing_table(self):
        table = {}
        headers = ["State"] + self.grammar["T"] + self.grammar["NT"] + ["$"]

        for i, state in enumerate(self.states):
            table[i] = {}
            for item in state:
                if "." in item[1] and item[1].index(".") == len(item[1]) - 1:
                    if item[0] == self.grammar["P"][0][0]:
                        table[i]["$"] = "Accept"
                    else:
                        for j, production in enumerate(self.grammar["P"]):
                            if item[0] == production[0]:
                                table[i]["$"] = f"Reduce {j}"
                else:
                    for symbol in self.grammar["items"]:
                        next_state = self.transitions[i].get(symbol)
                        if next_state is not None:
                            if symbol in self.grammar["T"]:
                                table[i][symbol] = f"Shift {next_state}"
                            elif symbol in self.grammar["NT"]:
                                table[i][symbol] = next_state

        # Create a list of rows for the table
        rows = []
        for i in range(len(self.states)):
            row = [f"I{i}"]
            for symbol in self.grammar["T"] + self.grammar["NT"] + ["$"]:
                action = table[i].get(symbol, "")
                row.append(action)
            rows.append(row)

        # Display the table using tabulate
        print(tabulate(rows, headers, tablefmt="grid"))
