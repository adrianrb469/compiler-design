from graphviz import Digraph

from automata.render import render_tree


class Node:
    pos_counter = 0

    def __init__(self, value, left=None, right=None, pos=None, nullable=None):
        self.value = value
        self.left = left
        self.right = right
        self.position = pos
        self.nullable = nullable
        self.firstPos = set()
        self.lastPos = set()


class SyntaxTree:
    def __init__(self, postfix):
        self.followPosTable = dict()
        self.posTable = dict()
        self.root = self.create_ast(postfix)
        self.operands = self.regexAlphabet(postfix)

    def regexAlphabet(self, postfix):
        alphabet = set()
        reserved = ["|", "*", ".", "ϵ", "ε"]

        i = 0
        while i < len(postfix):
            char = postfix[i]
            if char[0] == "\\":
                if len(char) > 1:
                    alphabet.add(char[1])
                else:
                    alphabet.add(char[0])
            elif char not in reserved:
                alphabet.add(char)
            i += 1
        return alphabet

    def create_ast(self, postfix):
        stack = []
        operators = ["|", "*", "."]

        Node.pos_counter = 0
        self.followPosTable = dict()
        self.posTable = dict()

        for char in postfix:
            new_node = Node(value=char)

            if char in operators:
                self.handle_operator(char, new_node, stack)
            else:
                self.handle_operand(char, new_node)

            stack.append(new_node)

        return stack[0] if stack else None

    def handle_operator(self, char, new_node, stack):
        new_node.right = stack.pop()
        if char != "*":
            new_node.left = stack.pop()

        if char == "|":
            self.handle_or_operator(new_node)
        elif char == ".":
            self.handle_dot_operator(new_node)
        else:  # char == '*'
            self.handle_star_operator(new_node)

    def handle_operand(self, char, new_node):
        if char == "ε":
            new_node.nullable = True
        else:
            if char[0] == "\\" and len(char) > 1:
                char = char[1]
                new_node.value = char

            Node.pos_counter += 1
            new_node.pos = Node.pos_counter
            self.followPosTable[new_node.pos] = set()

            self.posTable[char] = self.posTable.get(char, set())
            self.posTable[char].add(new_node.pos)

            new_node.nullable = False
            new_node.firstPos.add(new_node.pos)
            new_node.lastPos.add(new_node.pos)

    def handle_or_operator(self, new_node):
        new_node.nullable = new_node.left.nullable or new_node.right.nullable
        new_node.firstPos = new_node.left.firstPos.union(new_node.right.firstPos)
        new_node.lastPos = new_node.left.lastPos.union(new_node.right.lastPos)

    def handle_dot_operator(self, new_node):
        new_node.nullable = new_node.left.nullable and new_node.right.nullable

        if new_node.left.nullable:
            new_node.firstPos = new_node.left.firstPos.union(new_node.right.firstPos)
        else:
            new_node.firstPos = new_node.left.firstPos

        if new_node.right.nullable:
            new_node.lastPos = new_node.left.lastPos.union(new_node.right.lastPos)
        else:
            new_node.lastPos = new_node.right.lastPos

        for i in new_node.left.lastPos:
            self.followPosTable[i].update(new_node.right.firstPos)

    def handle_star_operator(self, new_node):
        new_node.nullable = True
        new_node.firstPos = new_node.right.firstPos
        new_node.lastPos = new_node.right.lastPos

        for i in new_node.lastPos:
            self.followPosTable[i].update(new_node.firstPos)

    def render(self, graph=None):
        render_tree(self.root)
