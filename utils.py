def print_definitions(definitions):
    print("Definitions: ")
    for name, value in definitions.items():
        print(f"{name} = {value}")

    print("\n")


def print_rules(rules):
    print("Rules: ")
    for name, value in rules.items():
        print(f"{value}")

    print("\n")


def format(regex):
    all_operators = ["|", "+", "?", "*"]
    binary_operators = ["|"]
    res = ""

    for i in range(len(regex)):
        c1 = regex[i]

        if i + 1 < len(regex):
            c2 = regex[i + 1]

            res += c1

            if (
                c1 != "("
                and c2 != ")"
                and c2 not in all_operators
                and c1 not in binary_operators
            ):
                res += "."

    res += regex[-1]
    return res


def shunting_yard(regex):
    precedence = {"|": 1, ".": 2, "*": 3, "+": 3, "?": 3}
    queue = []
    stack = []

    regex = format(regex)

    # CHAPUS
    hasHash = False
    if "#" in regex:
        hasHash = True
        regex = regex.replace("#", "")
    # CHAPUS

    for token in regex:
        if token.isalnum() or token in [
            "#",
            "ϵ",
        ]:
            queue.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                queue.append(stack.pop())
            stack.pop()
        else:
            while (
                stack
                and stack[-1] != "("
                and precedence[token] <= precedence[stack[-1]]
            ):
                queue.append(stack.pop())
            stack.append(token)

    while stack:
        queue.append(stack.pop())

    # CHAPUS
    print("regex:", regex)
    result = "".join(queue)
    result = result.replace("|.|", "||")
    if hasHash:
        result += "#."  # Add the # to the end of the expression
    # CHAPUS

    print("result:", result)

    return result


def add_concat(regex):
    output = ""
    operators = set([".", "|", "*", "(", ")"])  # regex operators
    for i in range(len(regex) - 1):
        output += regex[i]
        if (
            (regex[i] not in operators and regex[i + 1] not in operators)
            or (regex[i] not in operators and regex[i + 1] == "(")
            or (regex[i] == ")" and regex[i + 1] not in operators)
            or (regex[i] == "*" and regex[i + 1] not in operators)
            or (regex[i] == "*" and regex[i + 1] == "(")
        ):
            output += "."
    output += regex[-1]
    return output


def isValidExpression(expression):
    stack = []
    if expression == "" or expression.isspace():
        print("\tError: Empty expression")
        return False
    for char in expression:
        if not char.isalnum() and char not in {"*", "|", ".", "ϵ", "(", ")", "+", "?"}:
            print("\tError: Invalid character in expression")
            return False
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack or stack.pop() != "(":
                print("\tError: Unbalanced expression")
                return False
    balanced = len(stack) == 0
    if balanced:
        return True
    else:
        print("\tError: Unbalanced expression")
        return False
    # return len(stack) == 0
