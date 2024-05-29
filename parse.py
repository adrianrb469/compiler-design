import pickle

import LR0


def load_grammar(file_path):
    with open(file_path, "rb") as file:
        grammar = pickle.load(file)

    return grammar


def load_tokens(file_path):
    with open(file_path, "r") as file:
        tokens = file.read().split(",")

    return tokens


if __name__ == "__main__":

    grammar = load_grammar("grammar.pkl")
    lr0 = LR0.LR0(grammar)
    lr0.visualize().write_pdf("lr0_automata.pdf")
    print("LR0 saved in lr0_automata.pdf")
    lr0.slr1()

    tokens = load_tokens("tokens.txt")

    if tokens is None:
        print("No tokens found")
        exit(1)

    print("Tokens:")

    if lr0.parse(tokens, grammar["ignore"]):
        print("Accepted")
    else:
        print("Rejected")
