import string


class Regex:
    operators = ["|", "*", "?", "+"]
    precedence = {"(": 1, "|": 2, ".": 3, "*": 4, "?": 4, "+": 4}

    def __init__(self, regex) -> None:
        self.regex = regex
        self.tokens = self.tokenize(regex)
        self.formatted_regex = self.format()

    def tokenize(self, regex):
        tokens = []
        reserved = ['|','*','.','(',')','+','?',"'",'"']
        i = 0
        while i < len(regex):
            char = regex[i]

            if char == '\\':
                if i + 1 < len(regex):
                    #Interpretacion manual
                    if regex[i+1]=='s':
                        tokens.append(' ')
                    elif regex[i+1]=='t':
                        tokens.append('\t')
                    elif regex[i+1]=='n':
                        tokens.append('\n')
                    else:
                        tokens.append(regex[i+1] if regex[i+1] not in reserved else regex[i:i+2])
                    i += 2
                else:
                    tokens.append(char)
                    i += 1
            elif char=="'":
                if i + 2 < len(regex) and regex[i+2]=="'":
                    res = regex[i+1] if regex[i+1] not in reserved else '\\'+regex[i+1]
                    tokens.append(res)
                    i += 3 if i+3<len(regex) else len(regex)
                else:
                    tokens.append(char)
                    i += 1
            elif char == '"':
                _str = char
                i += 1
                
                first_i=i
                first_char = char
                
                while i < len(regex) and regex[i] != '"':
                    if regex[i] == '\\':
                        if i + 1 < len(regex):
                            if regex[i+1]=='s':
                                _str+=' '
                            elif regex[i+1]=='"':
                                _str+='"'
                            else:
                                _str+=regex[i+1] if regex[i+1] not in reserved else '\\'+regex[i+1]
                            
                            i += 1
                        else:
                            _str += regex[i]
                    else:
                        _str += regex[i]
                        
                    i += 1
                if i < len(regex): 
                    _str += regex[i]
                    _str = _str[1:-1]
                    j = 0
                    while j<len(_str):
                        if _str[j]=='\\':
                            
                            tokens.append('\\'+_str[j+1])
                            j+=1
                        else:
                            
                            tokens.append(_str[j])
                        j += 1
                    i+=1
                else:
                    tokens.append(first_char)
                    i=first_i
                    
            elif char == '[':
                clase_char = char
                i += 1
                
                first_i=i
                first_char = char
                while i < len(regex) and regex[i] != ']':
                    if regex[i] == '\\':
                        if i + 1 < len(regex):
                            if regex[i+1]=='s':
                                clase_char+=' '
                            elif regex[i+1]=='t':
                                clase_char+='\t'
                            elif regex[i+1]=='n':
                                clase_char+='\n'
                            elif regex[i+1]=='[':
                                clase_char+='['
                            elif regex[i+1]==']':
                                clase_char+=']'
                            else:
                                clase_char+=regex[i+1] if regex[i+1] not in reserved else '\\'+regex[i+1]
                            
                            i += 1
                        else:
                            clase_char += regex[i]
                    else:
                        clase_char += regex[i]
                        
                    i += 1
                if i < len(regex):  
                    clase_char += regex[i]
                    tokens.append(clase_char)
                    i += 1
                else:
                    tokens.append(first_char)
                    i=first_i
                    
            elif char in {'*', '+', '?', '|'}:
                tokens.append(char)
                i += 1

            elif char in {'(', ')'}:
                tokens.append(char)
                i += 1

            else:
                if char == ".":
                     # If the dot is not escaped, raise a ValueError
                     if i == 0 or regex[i - 1] != "\\":
                         raise ValueError("Dot must be escaped in regex")
    
                else:
                    tokens.append(char)
                    i += 1
            
        return tokens

    

    def format(self):
        allOperators = ['|', '?', '+', '*']
        binaryOperators = ['|']
        res = []
        
        tokens = self.tokens
        
        def handle_operator(index, operator, empty_symbol='ε'):
            nonlocal tokens
            if tokens[index - 1] != ')':
                if operator == '+':
                    tokens[index - 1:index + 1] = ['(',tokens[index - 1], tokens[index - 1], '*',')']
                elif operator == '?':
                    tokens[index - 1:index + 1] = ['(', tokens[index - 1], '|', empty_symbol, ')']
            else:
                j = index - 2
                count = 0
                while j >= 0 and (tokens[j] != '(' or count != 0):
                    if tokens[j] == ')':
                        count += 1
                    elif tokens[j] == '(':
                        count -= 1
                    j -= 1
                if tokens[j] == '(' and count == 0:
                    if operator == '+':
                        tokens[j:index + 1] = ['(']+tokens[j:index] + tokens[j:index] + ['*'] +[')']
                    elif operator == '?':
                        tokens[j:index + 1] = ['('] + tokens[j:index] + ['|', empty_symbol, ')']
        
        #Funcion para reconstruir todas las clases en un solo formato ["abc..."]
        def expand_character_class(char_class):
            characters = []
            complement = False
            i=0
            while i < len(char_class):
                c = char_class[i]
                if c=='^':
                    complement = True
                #Comillas simples
                elif c=="'":
                    if char_class[i+1]=='\\':
                        characters.append(char_class[i+2])
                        i+=1
                    else:
                        characters.append(char_class[i+1])
                    i+=2
                #Guion
                elif c=="-":
                    start = characters.pop()
                    end = char_class[i+2]
                    
                    for c in range(ord(start), ord(end) + 1):
                        characters.append(chr(c))
                    i+=3
                #Comillas dobles (sin escape de ")
                elif c=='"':
                    j=i+1
                    while j<len(char_class):
                        if char_class[j]!='"':
                            characters.append(char_class[j])
                        else:
                            break
                        j+=1
                    i=j
                i+=1
            
            if not complement:
                expanded = ''.join(item for item in characters)
                return expand_string('"'+expanded+'"')
            else:
                return None
            
                

        #Funcion para reconstruir la clase en formato ["abc.."] en (a|b|c...)    
        def expand_string(_str):
            reserved = ['|','*','.','(',')','+','?',"'",'"']
            expanded = []
            
            char_class = _str[1:-1]
            for c in char_class:
                if c in reserved:
                    expanded.append('\\'+c)
                else:
                    expanded.append(c)
                expanded.append('|')
            
            expanded.pop()
            return ['('] + [char for char in expanded] + [')']
        
        #Funcion para expandir (_)
        def expand_characters():
            characters = []
            reserved = ['|','*','.','(',')','+','?',"'",'"']
            caracteres_ascii = [chr(i) for i in range(32,127)]
            
            for c in caracteres_ascii:
                if c in reserved:
                    characters.append('\\'+c)
                elif c=='\\':
                    characters.append(str(ord(c)))
                else:
                    characters.append(c)
                characters.append('|')
            characters.pop()
            
            return ['('] + [char for char in characters] + [')']
                    

        i = 0
        while i < len(tokens):
            if tokens[i] == '+':
                handle_operator(i, '+')
                continue  
            i += 1

        i = 0
        while i < len(tokens):
            if tokens[i] == '?':
                handle_operator(i, '?')
                continue
            i += 1
            
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('[') and token.endswith(']'):
                expanded_tokens = expand_character_class(token)
                res.extend(expanded_tokens)
                
            elif token=='_':
                expanded_tokens = expand_characters()
                res.extend(expanded_tokens)
                
            else:
                res.append(token)
                
            if i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if token not in binaryOperators + ['('] and next_token not in allOperators + [')', '.']:
                    res.append('.')
            i += 1
            
        
        return res

    def shunting_yard(self):
        postfix, stack = [], []
        operators = ["|", "*", "."]

        regex = self.formatted_regex
        i = 0
        for char in regex:
            if char == "(":
                stack.append(char)
            elif char == ")":
                while stack and stack[-1] != "(":
                    postfix.append(stack.pop())

                if stack and stack[-1] == "(":
                    stack.pop()
                else:
                    raise ValueError("Mismatched parentheses.")
            elif char in operators:
                while stack and self.precedence.get(
                    stack[-1], 0
                ) >= self.precedence.get(char, 0):
                    postfix.append(stack.pop())
                stack.append(char)
            else:
                postfix.append(char)

            i += 1

        while len(stack) > 0:
            postfix.append(stack.pop())
            
        return postfix
