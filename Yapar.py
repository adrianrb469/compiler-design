import os
import re


class Yapar:
    """
    Parses a Yapar file, returning the grammar.
    """

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.tokens = []
        self.non_terminals = []
        self.productions = []
        self.items = []
        self.ignore = []
        self.parse()

    def parse(self) -> None:
        try:
            with open(self.filename, "r") as file:
                grammar = file.read()

            token_section, production_section = grammar.split("%%")

            token_pattern = r"%token\s+(.*?)(?=\n%token|\n%%|\nIGNORE|\n|$)"
            tokens = re.findall(token_pattern, token_section)

            ignore_pattern = r"IGNORE\s+(\w+)"
            ignored_tokens = re.findall(ignore_pattern, token_section)

            print("Ignored tokens:", ignored_tokens)
            self.ignore = ignored_tokens

            self.tokens = [token for token in tokens if token not in ignored_tokens]

            # if any token has a space, we split it (multiple tokens in one line...)
            self.tokens = [symbol for token in self.tokens for symbol in token.split()]

            rule_pattern = r"(\w+)\s*:\s*(.*?)\s*;"
            rules = re.findall(rule_pattern, production_section, re.DOTALL)

            for rule in rules:
                non_terminal, prod_str = rule
                prod_str = prod_str.strip()

                # we split by '|'
                prod_alternatives = prod_str.split("|")

                for prod in prod_alternatives:
                    symbols = prod.strip().split()
                    self.productions.append([non_terminal, symbols])

                    if non_terminal not in self.non_terminals:
                        self.non_terminals.append(non_terminal)

            self.items = self.non_terminals + self.tokens

        except FileNotFoundError:
            print(f"File {self.filename} not found.")
            return

    def get_grammar(self) -> dict:
        return {
            "T": self.tokens,
            "NT": self.non_terminals,
            "P": self.productions,
            "items": self.items,  # items = NT + T, in other words, all symbols
            "ignore": self.ignore,
        }
