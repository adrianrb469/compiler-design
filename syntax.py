from LR0 import LR0
from Yalex import Yalex
from Yapar import Yapar

LEXER = "yal/slr-1.yal"
PARSER = "yalp/actionable.yalp"


def print_grammar(grammar):

    print("Grammar:")
    print("Terminals:")
    print(grammar["T"], "\n")
    print("Non-terminals:")
    print(grammar["NT"], "\n")

    print("Productions:")
    for production in grammar["P"]:
        print(f"  {production[0]} -> {' '.join(production[1])}")
    print("\n")


def main(skip_lex=False):

    yapar = Yapar(PARSER)
    grammar = yapar.get_grammar()

    if not skip_lex:
        yalex = Yalex(LEXER, debug=False)
        pre_lex_tokens = [value for key, value in yalex.tokens if key != ""]

        # hack, we get the returned token separating the values by spaces, and getting the last one
        lex_tokens = [token.split(" ")[-1] for token in pre_lex_tokens]

        print("Tokens in lexer:")
        print(lex_tokens, "\n")
        for terminal in grammar["T"]:
            if terminal not in lex_tokens:
                raise Exception(f"Terminal {terminal} not in lexer tokens")

    print_grammar(grammar)

    lr0 = LR0(grammar)

    lr0.visualize().write_pdf("lr0_automata.pdf")

    print("LR0 saved in lr0_automata.pdf")

    lr0.slr1()


if __name__ == "__main__":
    main(skip_lex=True)
