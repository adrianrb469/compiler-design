import re
from Regex import Regex
from directConstruction import DirectDFA
from syntax_tree import SyntaxTree
from utils import print_definitions, print_rules


class Yalex:
    def __init__(self, filename: str) -> None:
        self.definitions = {}
        self.rules = {}
        self.parse_definitions(filename)
        # self.parse_rules(filename)

        self.parse_rules2(filename)

        print_definitions(self.definitions)
        print_rules(self.rules)

        def replace_keywords(rule):
            if rule in self.definitions:
                return f"({self.definitions[rule]})"
            return rule

        self.final_regex = "|".join(
            replace_keywords(rule) for rule in self.rules.values()
        )

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
                    _, line = line.split("let", 1)
                    current_key, current_value = line.split("=", 1)
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

    def parse_rules2(self, filename: str) -> None:
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

        # Trim, remove the part inside {}, remove single quotes, double quotes
        tokens = [
            token.split("{")[0].strip().strip("'").strip('"').replace("\\", "")
            for token in tokens
        ]

        # escape regex special characters
        tokens = [re.escape(token) for token in tokens]
        self.rules = dict(enumerate(tokens))

    def parse_rules(self, filename: str) -> None:
        with open(filename, "r") as file:
            content = file.read()

        # Find the line containing the keyword "rule"
        rule_index = content.find("rule")
        if rule_index == -1:
            return []

        # Extract the content after the "rule" line
        content = content[rule_index:]

        pattern = (
            r"(\w+)\s*\{\s*return\s*(\w+)\s*\}|\'([^\'\\])\'\s*\{\s*return\s*(\w+)\s*\}"
        )
        matches = re.findall(pattern, content)

        tokens = []
        for match in matches:
            print(match)
            if match[0]:
                token_name = match[0]
                token_value = token_name
            else:
                token_name = match[3]
                token_value = match[2]
                if token_value in ["+", "-", "*", "/", "(", ")"]:
                    token_value = f"\\{token_value}"

            tokens.append((token_name, token_value))

        self.rules = dict(tokens)
