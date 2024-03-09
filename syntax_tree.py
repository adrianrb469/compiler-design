from node import Node

# from utils import shunting_yard
from render import render_tree


class SyntaxTree:
    def __init__(self, regex):
        self.operands = self.getOperands(regex)
        # self.regex = shunting_yard(regex)
        self.regex = regex
        self.root = self.syntax_tree(self.regex)
        self.node_map = populate_node_map(self.root)
        calc_nullable(self.root)
        calc_firstpos(self.root)
        calc_lastpos(self.root)
        calc_followpos(self.root)

    def syntax_tree(self, expression):
        stack = []
        for char in expression:
            if char not in {"*", "|", "."}:
                stack.append(Node(char))
            else:
                if char == "*":
                    operand = stack.pop()
                    stack.append(Node(char, operand))

                else:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(Node(char, left, right))

        return stack.pop()  # The final syntax tree root node

    def getOperands(self, regex):
        operands = set()
        for char in regex:
            if char not in {"*", "|", ".", "ϵ", "(", ")"}:
                operands.add(char)
        return operands

    def render(self):
        render_tree(self.root)
        return node_map


node_map = {}


def populate_node_map(node):
    if node is None:
        return

    if node.value not in {"*", "|", ".", "?"}:  # Leaf node
        node_map[node.id] = node
    # Recursively populate the map for all nodes
    populate_node_map(node.left)
    populate_node_map(node.right)
    return node_map


def calc_nullable(node):
    if node is None:
        return
    # Leafs :)
    if node.value not in {"*", "|", ".", "ϵ"}:
        node.nullable = False
    else:
        calc_nullable(node.left)
        calc_nullable(node.right)
        if node.value == "*" or node.value == "ϵ":
            node.nullable = True
        elif node.value == "|":
            node.nullable = node.left.nullable or node.right.nullable
        elif node.value == ".":
            node.nullable = node.left.nullable and node.right.nullable


def calc_firstpos(node):
    if node is None:
        return set()
    if node.value not in {"*", "|", ".", "ϵ"}:
        node.firstpos = {node.id}
    else:
        left_firstpos = calc_firstpos(node.left)
        right_firstpos = calc_firstpos(node.right) if node.right else set()

        if node.value == "|":
            node.firstpos = left_firstpos.union(right_firstpos)
        elif node.value == ".":
            if node.left and node.left.nullable:
                node.firstpos = left_firstpos.union(right_firstpos)
            else:
                node.firstpos = left_firstpos
        elif node.value == "*":
            node.firstpos = left_firstpos

    return node.firstpos


def calc_lastpos(node):
    if node is None:
        return set()
    if node.value not in {"*", "|", ".", "ϵ"}:
        node.lastpos = {node.id}
    else:
        left_lastpos = calc_lastpos(node.left)
        right_lastpos = calc_lastpos(node.right) if node.right else set()

        if node.value == "|":
            node.lastpos = left_lastpos.union(right_lastpos)
        elif node.value == ".":
            if node.right and node.right.nullable:
                node.lastpos = left_lastpos.union(right_lastpos)
            else:
                node.lastpos = right_lastpos
        elif node.value == "*":
            node.lastpos = left_lastpos
    return node.lastpos


def calc_followpos(node):
    if node is None:
        return

    calc_followpos(node.left)
    calc_followpos(node.right)

    if node.value == ".":
        for position in node.left.lastpos:
            node_map[position].followpos.update(node.right.firstpos)
    elif node.value == "*":
        for position in node.lastpos:
            node_map[position].followpos.update(node.firstpos)
