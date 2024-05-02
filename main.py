from Regex import Regex
from Yalex import Yalex
from syntax_tree import SyntaxTree
from directDfa import DirectDFA
from pickle import dump

yalex = Yalex("examples/python.yal")
print("Tokens: \n", yalex.tokens, "\n")
print("Final Regex: \n", yalex.final_regex)

postfix = Regex(yalex.final_regex).shunting_yard()
tree = SyntaxTree(postfix)
# tree.render()


dfa = DirectDFA()
dfa.generate_direct_dfa(tree,tree.root)
dfa.set_actions(yalex.tokens)
# dfa.render()

content = f"""# Scanner generated automatically by Yalex. Do not modify this file.
import pickle
{yalex.header}
def execute_action(action, token):
    local_namespace = {{}}

    function_code = f'def temporary_function():\\n'
    if action:
        function_code += f'    {{action}}\\n'
    else:
        print("Empty action detected for token:", token)
        function_code += f'    pass\\n'

    function_code += 'result = temporary_function()'

    try:
        exec(function_code, globals(), local_namespace)
        return local_namespace['result']
    except Exception as e:
        print(f"Error executing the action: {{e}}")
        return None

def recognize_tokens(dfa, file_path):
    # Read the file
    with open(file_path, "r") as file:
        data = file.read()
        
    i = 0
    length_data = len(data)
    current_state = dfa.initial_state
    current_token = ""
    last_valid_token = ""
    last_valid_state = None
    
    while i < length_data:
        char = data[i]
        if char in current_state.transitions:
            current_state = current_state.transitions[char]
            current_token += char
            i += 1
            if current_state.accepting:
                last_valid_token = current_token
                last_valid_state = current_state
        else:
            if last_valid_token:
                # Perform action associated with the last valid state
                action_result = execute_action(last_valid_state.action, last_valid_token)
                if action_result is not None:
                    print(action_result)
                current_state = dfa.initial_state
                print("Token:", last_valid_token)
                current_token = ""
                last_valid_token = ""
                last_valid_state = None
            else:
                # No valid transition found, report an error
                print("Lexical error:", char, "at position", i)
                # Move to the next character
                i += 1
                current_state = dfa.initial_state
                current_token = ""
                last_valid_token = ""
                last_valid_state = None
    
    if last_valid_state:
        action_result = execute_action(last_valid_state.action, last_valid_token)
        if action_result is not None:
            print(action_result)
        

with open("dfa.pkl", "rb") as file:
    dfa = pickle.load(file)

recognize_tokens(dfa, "python.txt")
    
{yalex.trailer}
"""

# Save the DFA to a pickle file
with open("dfa.pkl", "wb") as file:
    dump(dfa, file)

# Write the content to a file
with open("Scan.py", "w") as file:
    file.write(content)
    
print("\nScan.py generated in current directory.")
    