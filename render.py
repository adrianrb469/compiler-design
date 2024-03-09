import re
import string
import pydotplus


def render_tree(root):
    graph = create_graph(root)
    graph.write_png("result/tree.png")
    graph.write_svg("result/tree.svg")
    return graph


counter = [0]  # Use a list so that the counter is mutable


def add_edges(graph, node, parent_id=None):
    if node is not None:
        node_id = str(counter[0])
        counter[0] += 1

        # if node value is whitespace, newline or tab, replace it with the corresponding escape sequence

        if (len(node.value)) == 1:
            # if its printable leave it as it is

            if node.value in {
                ",",
                "(",
                ")",
                "*",
                "+",
                ".",
                "|",
                "?",
                "\\",
                "[",
                "]",
                "{",
                "}",
                "^",
                "$",
                "-",
            }:
                node.value = "\\" + node.value
        elif len(node.value) > 1:
            # if it has \ before it, remove it
            if node.value[0] == "\\":
                node.value = node.value[1:]
            # if its tab or space replace with "SPACE" or "TAB"
            if node.value == " ":
                node.value = "SPACE"
            elif node.value == "\t":
                node.value = "TAB"

        # if node.value in {"(", ")", "*", "+", ".", "|"}:
        #     node.value = "\\" + node.value
        graph.add_node(pydotplus.Node(node_id, label=node.value, shape="circle"))
        if parent_id is not None:
            graph.add_edge(pydotplus.Edge(parent_id, node_id))
        add_edges(graph, node.left, node_id)
        add_edges(graph, node.right, node_id)


def create_graph(root):
    graph = pydotplus.Dot(graph_type="graph")
    add_edges(graph, root)
    return graph


def create_direct_dfa_graph(states, transitions, minimized=False):
    # Convert sets to strings
    # states = [str(state) for state in states]
    # start_state = str(start_state)
    # acceptance_states = [state for state in acceptance_states]

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("LR")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    # Create nodes for each state
    state_nodes = {}
    num = 0
    for state in states:
        if state.state != {"Ø"}:
            node = pydotplus.Node(num)
            node.set_name(str(state.state))
            if state.initial:
                # node.set_name("Start")
                node.set_shape("circle")
                node.set_style("filled")

            if state.accepting:
                node.set_shape("doublecircle")  # Final states are double circled
            node.set_fontsize(12)  # Set font size
            node.set_width(0.6)  # Set the desired width
            node.set_height(0.6)  # Set the desired height
            state_nodes[str(state.state)] = node
            # print(state.state)
            dot.add_node(node)

            num += 1

    for transition in transitions:
        if (
            transition.symbol != "#"
            and str(transition.originState) in state_nodes
            and str(transition.destinationState) in state_nodes
        ):
            # print(transition.originState, transition.symbol, transition.destinationState)
            edge = pydotplus.Edge(
                state_nodes[str(transition.originState)],
                state_nodes[str(transition.destinationState)],
                label=str(transition.symbol),
            )
            dot.add_edge(edge)

    pydotplus.find_graphviz()

    graph = dot

    # Save or display the graph
    if not minimized:
        png_file_path = "result/direct_dfa.png"
    else:
        png_file_path = "result/min_direct_dfa.png"
    graph.write_png(png_file_path)  # Save PNG file


def render_nfa(nfa):
    graph = pydotplus.Dot(graph_type="digraph")
    graph.set_rankdir("LR")
    added_states = set()
    graph.set_prog("neato")

    def add_states(state):
        if state.id in added_states:
            return
        added_states.add(state.id)
        graph.add_node(
            pydotplus.Node(
                str(state.id),
                shape="doublecircle" if state == nfa.final_state else "circle",
            )
        )
        for transition in state.transitions:
            graph.add_edge(
                pydotplus.Edge(
                    str(state.id),
                    str(transition.new_state.id),
                    label=str(transition.input),
                )
            )
            add_states(transition.new_state)

    add_states(nfa.initial_state)

    graph.write_png("result/nfa.png")
    graph.write_svg("result/nfa.svg")


def render_dfa(dfa, name="dfa"):
    graph = pydotplus.Dot(graph_type="digraph")
    graph.set_rankdir("LR")
    graph.set_prog("neato")

    seen_states = set()

    for dfa_state in dfa.states:
        # If the state has no transitions and it's not an accepting state, skip it
        if not dfa_state.transitions and not dfa_state.is_accepting:
            continue

        if dfa_state.id not in seen_states:
            graph.add_node(
                pydotplus.Node(
                    str(dfa_state.id),
                    shape="doublecircle" if dfa_state.is_accepting else "circle",
                    style="filled" if dfa_state.is_start else "",
                )
            )
            seen_states.add(dfa_state.id)

        for input, new_dfa_state in dfa_state.transitions.items():
            if new_dfa_state.id not in seen_states:
                graph.add_node(
                    pydotplus.Node(
                        str(new_dfa_state.id),
                        shape="doublecircle"
                        if new_dfa_state.is_accepting
                        else "circle",
                        style="filled" if new_dfa_state.is_start else "",
                    )
                )
                seen_states.add(new_dfa_state.id)

            graph.add_edge(
                pydotplus.Edge(
                    str(dfa_state.id),
                    str(new_dfa_state.id),
                    label=str(input),
                )
            )

    graph.write_png(f"result/{name}.png")
    graph.write_svg(f"result/{name}.svg")
