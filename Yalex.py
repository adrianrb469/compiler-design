import re

from automata.directDfa import DirectDFA
from automata.Regex import Regex
from automata.syntax_tree import SyntaxTree
from utils import print_definitions, print_rules


class Yalex:
    """
    Parses a Yalex file, returning the final regex and the rules.
    """

    def __init__(self, filename: str, debug=False):
        self.definitions = {}
        self.rules = {}
        self.debug = debug
        self.parse_definitions(filename)
        self.parse_rules(filename)
        self.parse_header(filename)
        self.parse_trailer(filename)

        if self.debug:

            print_definitions(self.definitions)

        def replace_keywords(rule):
            if rule in self.definitions:
                return self.definitions[rule]
            return rule

        self.final_regex = (
            "("
            + "|".join(
                replace_keywords(rule[0]) + "※"
                for rule in self.rules.values()
                if rule[0] != ""
            )
            + ")"
        )
        self.tokens = [(v[0], v[1]) for k, v in self.rules.items() if v[0] != ""]

    def parse_header(self, filename: str) -> None:
        with open(filename, "r") as f:
            content = f.read()
            content_before_let = content.split("let")[
                0
            ]  # split on "let" and take the first part
            if "{" in content_before_let and "}" in content_before_let:
                header = content_before_let.split("{")[1].split("}")[
                    0
                ]  # split on "{" and "}" as before
                if self.debug:
                    print("Header: ", header)
                self.header = header
            else:
                self.header = ""
                print("No header found in the file.\n")

    def parse_trailer(self, filename: str) -> None:
        with open(filename, "r") as f:
            content = f.read()
            # get content of last "{" and "}" of the file
            content_after_let = content.split("let")[-1]

            if "{" in content_after_let and "}" in content_after_let:
                trailer = content_after_let.split("{")[-1].split("}")[0]

                self.trailer = trailer
                if self.debug:
                    print("Trailer: ", trailer)

    def parse_definitions(self, filename: str) -> None:
        with open(filename, "r") as f:
            lines = f.readlines()

            current_key = None
            current_value = ""

            for line in lines:
                if line.startswith("rule"):
                    break

                line = line.strip()
                if line.startswith("let"):
                    if current_key is not None:
                        self.definitions[current_key] = current_value.strip()
                    try:
                        _, line = line.split("let", 1)
                        current_key, current_value = line.split("=", 1)
                    except ValueError:
                        raise ValueError("Malformed definition")
                    current_key = current_key.strip()
                    current_value = current_value.strip()
                else:
                    current_value += " " + line

            if current_key is not None:
                self.definitions[current_key] = current_value.strip()

        def format_definitions(definitions):
            for def_name, def_value in reversed(definitions.items()):
                for name, definition in definitions.items():
                    definitions[name] = definition.replace(def_name, def_value)
            return definitions

        for definition in self.definitions.values():
            if not definition.strip():
                raise ValueError("Empty definition")

        self.definitions = format_definitions(self.definitions)

    def parse_rules(self, filename: str) -> None:
        with open(filename, "r") as file:
            content = file.read()

            # Find the line containing the keyword "rule"
            rule_index = content.find("rule")

            # Find the "=" sign after "rule"
            equal_index = content.find("=", rule_index)

            # Get the tokens part
            tokens_part = content[equal_index + 1 :]

            # Split by '|'
            tokens = tokens_part.split("|")

            token_info = []
            for token in tokens:
                token = token.strip()
                if "{" in token and "}" in token:

                    token_parts = token.split("{")
                    token_regex = token_parts[0].strip().replace("\\", "")
                    token_action = token_parts[1].split("}")[0].strip()
                    token_info.append((token_regex, token_action))
                else:
                    token_regex = token.strip().replace("\\", "")
                    token_info.append((token_regex, None))

            self.rules = dict(enumerate(token_info))
