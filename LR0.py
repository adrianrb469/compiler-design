from typing import Dict, List, Tuple, Union

import pydotplus
from tabulate import tabulate

Production = Tuple[str, List[str]]  # (NT, [symbols])
Grammar = Dict[str, Union[List[str], List[Production]]]

EPSILON = "ε"


class LR0:
    """
    LR(0) parser generator, based on the grammar provided.

    """

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.table = {}
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
                        if dot_pos < len(item[1]) - 2 and item[1][dot_pos + 2] == "ε":
                            # If ε is found after the symbol, move the dot two positions to the right
                            new_item = [
                                item[0],
                                item[1][:dot_pos]
                                + [item[1][dot_pos + 1], ".", "ε"]
                                + item[1][dot_pos + 3 :],
                            ]
                        else:
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

    def first(self):
        first_sets = {nt: set() for nt in self.grammar["NT"]}
        while True:
            updated = False
            for production in self.grammar["P"]:
                nt, rhs = production
                for symbol in rhs:
                    if symbol in self.grammar["T"]:
                        if symbol not in first_sets[nt]:
                            first_sets[nt].add(symbol)
                            updated = True
                        break
                    elif symbol in self.grammar["NT"]:
                        if (
                            first_sets[symbol]
                            .difference({"ε"})
                            .issubset(first_sets[nt])
                        ):
                            break
                        else:
                            first_sets[nt].update(first_sets[symbol].difference({"ε"}))
                            updated = True
                            if "ε" not in first_sets[symbol]:
                                break
                else:
                    if "ε" not in first_sets[nt]:
                        first_sets[nt].add("ε")
                        updated = True
            if not updated:
                break
        return first_sets

    def follow(self, first_sets):
        follow_sets = {nt: set() for nt in self.grammar["NT"]}
        follow_sets[self.grammar["P"][0][0]].add("$")
        while True:
            updated = False
            for production in self.grammar["P"]:
                nt, rhs = production
                for i in range(len(rhs)):
                    if rhs[i] in self.grammar["NT"]:
                        if i == len(rhs) - 1:
                            if follow_sets[nt].difference(follow_sets[rhs[i]]):
                                follow_sets[rhs[i]].update(follow_sets[nt])
                                updated = True
                        else:
                            next_symbol = rhs[i + 1]
                            if next_symbol in self.grammar["T"]:
                                if next_symbol not in follow_sets[rhs[i]]:
                                    follow_sets[rhs[i]].add(next_symbol)
                                    updated = True
                            elif next_symbol in self.grammar["NT"]:
                                if (
                                    first_sets[next_symbol]
                                    .difference({"ε"})
                                    .difference(follow_sets[rhs[i]])
                                ):
                                    follow_sets[rhs[i]].update(
                                        first_sets[next_symbol].difference({"ε"})
                                    )
                                    updated = True
                                if "ε" in first_sets[next_symbol]:
                                    if follow_sets[nt].difference(follow_sets[rhs[i]]):
                                        follow_sets[rhs[i]].update(follow_sets[nt])
                                        updated = True
            if not updated:
                break
        return follow_sets

    def slr1(self):
        headers = ["State"] + self.grammar["T"] + ["$"] + self.grammar["NT"]

        first_sets = self.first()
        follow_sets = self.follow(first_sets)

        for i, state in enumerate(self.states):
            self.table[i] = {}
            for item in state:
                if "." in item[1] and item[1].index(".") == len(item[1]) - 1:
                    if item[0] == self.grammar["P"][0][0]:
                        self.table[i]["$"] = "Accept"
                    else:
                        for j, production in enumerate(self.grammar["P"]):
                            if (
                                item[0] == production[0]
                                and item[1][:-1] == production[1]
                            ):
                                for symbol in follow_sets[item[0]]:

                                    # We check if theres already a value in the table, meaning a conflict
                                    if (
                                        symbol in self.table[i]
                                        and self.table[i][symbol] != f"R{j}"
                                    ):
                                        raise ValueError(
                                            f"Reduce-Reduce conflict in state I{i} for symbol {symbol}"
                                        )

                                    if (
                                        symbol in self.table[i]
                                        and self.table[i][symbol] == f"R{j}"
                                    ):
                                        raise ValueError(
                                            f"Shift-Reduce conflict in state I{i} for symbol {symbol}"
                                        )

                                    self.table[i][symbol] = f"R{j}"
                else:
                    dot_pos = item[1].index(".")
                    next_symbol = item[1][dot_pos + 1]
                    if next_symbol in self.grammar["T"] + ["$"]:
                        next_state = self.transitions[i].get(next_symbol)
                        if next_state is not None:
                            self.table[i][next_symbol] = f"S{next_state}"
                    elif next_symbol in self.grammar["NT"]:
                        next_state = self.transitions[i].get(next_symbol)
                        if next_state is not None:
                            self.table[i][next_symbol] = next_state

        # Create a list of rows for the self.table
        rows = []
        for i in range(len(self.states)):
            row = [f"I{i}"]
            for symbol in self.grammar["T"] + ["$"]:
                action = self.table[i].get(symbol, "")
                row.append(action)
            for symbol in self.grammar["NT"]:
                goto = self.table[i].get(symbol, "")
                row.append(goto)
            rows.append(row)

        # Display the table using tabulate
        print(tabulate(rows, headers, tablefmt="grid"))

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

            state_label += "<TR><TD COLSPAN='2'><B>Kernel:</B></TD></TR>\n"
            for item in kernel_items:
                state_label += (
                    f"<TR><TD>{item[0]}</TD><TD>{' '.join(item[1])}</TD></TR>\n"
                )

            state_label += "<TR><TD COLSPAN='2'><B>Closure:</B></TD></TR>\n"
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

    def parse(self, tokens: List[str], ignore: List[str]) -> bool:
        stack = [0]
        tokens.append("$")
        token_index = 0

        while True:

            top = stack[-1]
            symbol = tokens[token_index]

            if symbol in ignore:
                token_index += 1
                continue

            action = self.table[top].get(symbol)

            if action is None:
                return False  # Input is not accepted

            if action == "Accept":
                return True  # Input is successfully parsed

            if action.startswith("S"):
                state = action[1:]
                stack.extend([symbol, int(state)])
                token_index += 1
            elif action.startswith("R"):
                rule = action[1:]
                nt, rhs = self.grammar["P"][int(rule)]
                stack = stack[: -2 * len(rhs)]  # Pop 2*len(β) symbols off the stack
                top = stack[-1]
                stack.extend([nt, self.table[top][nt]])
