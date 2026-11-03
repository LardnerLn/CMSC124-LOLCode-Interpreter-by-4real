class SyntaxErrorLOL(Exception):
    # Custom exception for syntax errors with line numbers
    pass

indent_level = 0

def print_tree(node_name):
    #for parse tree printing
    global indent_level
    prefix = "│   " * indent_level + "├── "
    print(f"{prefix}{node_name}")

# Global parser state
tokens = []
pos = 0

# =========================================================
# Helper functions for token stream navigation
def current_token():
    # Returns the token tuple at the current position, or None if at end of file
    parse_comments()
    if pos < len(tokens):
        return tokens[pos]
    return None

def peek_lexeme():
    # Returns the text (lexeme) of the current token
    token = current_token()
    if token:
        return token[1]
    else:
        None

def peek_category():
    # Returns the classification category of the current token
    token = current_token()
    if token:
        return token[2]
    else:
        None

def advance():
    # Moves the pointer forward by one token.
    global pos
    token = current_token()
    pos += 1
    return token

def match(expected_lexeme):
    # Advances and returns the token if it matches the expected lexeme
    token = current_token()
    if token and token[1] == expected_lexeme:
        advance()
        return token
    return None

def expect(expected_lexeme, error_context=""):
    # Enforces that the current token is equal to expected_lexeme, or throws SyntaxErrorLOL
    token = match(expected_lexeme)
    if not token:
        curr = current_token()
        if curr:
            line, lexeme, _ = curr
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected '{expected_lexeme}', but found '{lexeme}'. {error_context}")
        else:
            raise SyntaxErrorLOL(f"Syntax Error at end of file: Expected '{expected_lexeme}'. {error_context}")
    return token

# =========================================================
def parse(token_list):
    # Initializes global token state and starts top level parsing
    global tokens, pos, indent_level
    tokens = token_list
    pos = 0
    indent_level = 0
    
    print("\n================ PARSE TREE / GRAMMAR STRUCTURE ================")
    result = parse_program()
    print("================================================================")
    return result

# =========================================================
def parse_program():
    # <program> ::= HAI <wazzup-sec> <statement-block> KTHXBYE
    global indent_level
    print_tree("<program>")
    indent_level += 1

    expect("HAI", "Program must start with 'HAI'.")
    print_tree("HAI")

    # Optional WAZZUP block
    if peek_lexeme() == "WAZZUP":
        parse_wazzup_block()

    # Parse main body statements until KTHXBYE
    while current_token() and peek_lexeme() != "KTHXBYE":
        parse_statement()

    expect("KTHXBYE", "Program must end with 'KTHXBYE'.")
    print_tree("KTHXBYE")

    if current_token():
        line, lexeme, _ = current_token()
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected token '{lexeme}' after KTHXBYE.")

    indent_level -= 1

    return

# =========================================================
def parse_wazzup_block():
    # <wazzup-sec> ::= WAZZUP <var-declaration>* BUHBYE
    global indent_level
    print_tree("<wazzup-sec>")
    indent_level += 1

    expect("WAZZUP", "Expected 'WAZZUP' to start variable declaration section.")
    print_tree("WAZZUP")

    while current_token() and peek_lexeme() != "BUHBYE":
        parse_var_declaration()

    expect("BUHBYE", "Expected 'BUHBYE' to close variable declaration section.")
    print_tree("BUHBYE")
    indent_level -= 1

# =========================================================
def parse_var_declaration():
    # <var-declaration> ::= I HAS A <var-identifier> [ITZ <expr>]
    global indent_level
    print_tree("<var-declaration>")
    indent_level += 1

    expect("I HAS A", "Variable declaration must start with 'I HAS A'.")
    print_tree("I HAS A")

    curr = current_token()
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        found = f"'{curr[1]}'" if curr else "end of file"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected variable name after 'I HAS A', found {found}.")
    
    print_tree(f"Identifier: {curr[1]}")
    advance()  # consume variable identifier

    if match("ITZ"):
        print_tree("ITZ")
        indent_level += 1
        parse_expression()
        indent_level -= 1

    indent_level -= 1

# =========================================================
def parse_statement():
    # Parses individual statements based on key tokens
    token = current_token()
    if not token:
        return

    lexeme = token[1]

    if lexeme == "VISIBLE":
        parse_visible()
    elif lexeme == "GIMMEH":
        parse_gimmeh()
    elif lexeme == "O RLY?":
        parse_if_statement()
    elif lexeme == "WTF?":
        parse_switch_statement()
    elif lexeme == "IM IN YR":
        parse_loop_statement()
    elif lexeme == "HOW IZ I":
        parse_function_definition()
    elif token[2] == "Identifier":
        global indent_level
        print_tree("<assignment>")
        indent_level += 1
        
        # Check if assignment (var R expr) or re-casting (var IS NOW A type)
        var_tok = advance()
        print_tree(f"Identifier: {var_tok[1]}")
        next_lexeme = peek_lexeme()

        if next_lexeme == "R":
            match("R")
            print_tree("R")
            indent_level += 1
            parse_expression()
            indent_level -= 1
        elif next_lexeme == "IS NOW A":
            match("IS NOW A")
            print_tree("IS NOW A")
            if peek_category() != "Data Type":
                line = current_token()[0] if current_token() else "EOF"
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected data type after 'IS NOW A'.")
            dt_tok = advance()
            print_tree(f"Data Type: {dt_tok[1]}")
        else:
            line = token[0]
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected identifier statement with '{lexeme}'.")
        indent_level -= 1
    else:
        # Standalone expression statement (result saved in IT)
        parse_expression()

# =========================================================
def parse_visible():
    # <print> ::= VISIBLE <expr> (+ <expr>)*
    global indent_level
    print_tree("<output-statement>")
    indent_level += 1

    expect("VISIBLE")
    print_tree("VISIBLE")
    
    indent_level += 1
    parse_expression()
    indent_level -= 1

    while match("+"):
        print_tree("+")
        indent_level += 1
        parse_expression()
        indent_level -= 1
        
    indent_level -= 1

# =========================================================
def parse_gimmeh():
    # <input> ::= GIMMEH <var-identifier>
    global indent_level
    print_tree("<input-statement>")
    indent_level += 1

    expect("GIMMEH")
    print_tree("GIMMEH")
    
    curr = current_token()
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'GIMMEH' requires a variable identifier.")
    
    print_tree(f"Identifier: {curr[1]}")
    advance()
    indent_level -= 1

# =========================================================
def parse_comments():
    # <comment> ::= BTW | OBTW TLDR  
    global pos
    while pos < len(tokens):
        line, lexeme, _ = tokens[pos]
 
        if lexeme == "BTW":
            pos += 1
        elif lexeme == "OBTW":
            pos += 1
            if pos < len(tokens) and tokens[pos][1] == "TLDR":
                pos += 1
            else:
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'OBTW' has no closing 'TLDR'.")
        elif lexeme == "TLDR":
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'TLDR' found without a matching 'OBTW'.")
        else:
            break

# =========================================================
def parse_expression():
    # Parses prefix operations, literals, identifiers, typecasts, and function calls
    global indent_level
    curr = current_token()
    if not curr:
        raise SyntaxErrorLOL("Syntax Error: Unexpected end of tokens while parsing expression.")

    lexeme, category = curr[1], curr[2]

    # 1. Literals and Identifiers
    if category in ["Literal", "Literal (NUMBR)", "Literal (NUMBAR)", "Literal (YARN)", "Literal (TROOF)", "Identifier"]:
        print_tree(f"Expression ({lexeme})")
        advance()
        return

    # 2. Arithmetic Operations
    if lexeme in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        print_tree("AN")
        parse_expression()
        indent_level -= 1
        return

    # 3. Boolean Operations
    if lexeme in ["BOTH OF", "EITHER OF", "WON OF"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        print_tree("AN")
        parse_expression()
        indent_level -= 1
        return

    if lexeme == "NOT":
        print_tree("NOT")
        advance()
        indent_level += 1
        parse_expression()
        indent_level -= 1
        return

    if lexeme in ["ALL OF", "ANY OF"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        parse_expression()
        expect("AN", f"Expected 'AN' in {lexeme} clause.")
        print_tree("AN")
        parse_expression()
        while match("AN"):
            print_tree("AN")
            parse_expression()
        expect("MKAY", f"Expected 'MKAY' to close {lexeme} expression.")
        print_tree("MKAY")
        indent_level -= 1
        return

    # 4. Comparison Operations
    if lexeme in ["BOTH SAEM", "DIFFRINT"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} comparison.")
        print_tree("AN")
        parse_expression()
        indent_level -= 1
        return

    # 5. String Concatenation
    if lexeme == "SMOOSH":
        print_tree("SMOOSH")
        advance()
        indent_level += 1
        parse_expression()
        expect("AN", "Expected 'AN' after first SMOOSH operand.")
        print_tree("AN")
        parse_expression()
        while match("AN"):
            print_tree("AN")
            parse_expression()
        indent_level -= 1
        return

    # 6. Typecasting
    if lexeme == "MAEK":
        print_tree("MAEK")
        advance()
        indent_level += 1
        parse_expression()
        expect("A", "Expected 'A' after expression in MAEK typecast.")
        print_tree("A")
        if peek_category() != "Data Type":
            raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Expected valid data type in MAEK casting.")
        print_tree(f"Data Type: {current_token()[1]}")
        advance()
        indent_level -= 1
        return

    # 7. Function Call
    if lexeme == "I IZ":
        print_tree("Function Call")
        advance()
        curr_id = current_token()
        if not curr_id or curr_id[2] != "Identifier":
            raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Expected function name after 'I IZ'.")
        print_tree(f"Function Name: {curr_id[1]}")
        advance()
        
        indent_level += 1
        if match("YR"):
            print_tree("YR")
            parse_expression()
            while match("AN") and match("YR"):
                print_tree("AN YR")
                parse_expression()
        indent_level -= 1

        expect("MKAY", "Expected 'MKAY' at end of function call.")
        print_tree("MKAY")
        return

    raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Invalid expression starting with '{lexeme}'.")

# =========================================================
def parse_if_statement():
    global indent_level
    print_tree("<if-statement>")
    indent_level += 1

    expect("O RLY?")
    print_tree("O RLY?")
    expect("YA RLY", "Expected 'YA RLY' after 'O RLY?'.")
    print_tree("YA RLY")

    indent_level += 1
    while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
        parse_statement()
    indent_level -= 1

    while peek_lexeme() == "MEBBE":
        advance()
        print_tree("MEBBE")
        indent_level += 1
        parse_expression()
        while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
            parse_statement()
        indent_level -= 1

    if match("NO WAI"):
        print_tree("NO WAI")
        indent_level += 1
        while current_token() and peek_lexeme() != "OIC":
            parse_statement()
        indent_level -= 1

    expect("OIC", "Expected 'OIC' to close conditional statement.")
    print_tree("OIC")
    indent_level -= 1

# =========================================================
def parse_switch_statement():
    global indent_level
    print_tree("<switch-statement>")
    indent_level += 1

    expect("WTF?")
    print_tree("WTF?")

    while peek_lexeme() == "OMG":
        advance()
        print_tree("OMG Case")
        indent_level += 1
        parse_expression()
        while current_token() and peek_lexeme() not in ["OMG", "OMGWTF", "OIC"]:
            if peek_lexeme() == "GTFO":
                advance()
                print_tree("GTFO")
            else:
                parse_statement()
        indent_level -= 1

    if match("OMGWTF"):
        print_tree("OMGWTF Default")
        indent_level += 1
        while current_token() and peek_lexeme() != "OIC":
            if peek_lexeme() == "GTFO":
                advance()
                print_tree("GTFO")
            else:
                parse_statement()
        indent_level -= 1

    expect("OIC", "Expected 'OIC' to close switch-case statement.")
    print_tree("OIC")
    indent_level -= 1

# =========================================================
def parse_loop_statement():
    global indent_level
    print_tree("<loop-statement>")
    indent_level += 1

    expect("IM IN YR")
    print_tree("IM IN YR")
    
    loop_label_token = current_token()
    if not loop_label_token or loop_label_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected loop label identifier.")

    print_tree(f"Label: {loop_label_token[1]}")
    loop_label = loop_label_token[1]
    advance()

    op = peek_lexeme()
    if op not in ["UPPIN", "NERFIN"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected 'UPPIN' or 'NERFIN' in loop operation.")
    print_tree(f"Operation: {op}")
    advance()

    expect("YR", "Expected 'YR' after loop operation.")
    var_token = current_token()
    if not var_token or var_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected variable identifier in loop operation.")
    print_tree(f"Loop Var: {var_token[1]}")
    advance()

    cond = peek_lexeme()
    if cond not in ["TIL", "WILE"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected 'TIL' or 'WILE' loop condition.")
    print_tree(f"Condition: {cond}")
    advance()
    
    indent_level += 1
    parse_expression()
    
    while current_token() and peek_lexeme() != "IM OUTTA YR":
        parse_statement()
    indent_level -= 1

    expect("IM OUTTA YR", "Expected 'IM OUTTA YR' to end loop.")
    end_label_token = current_token()
    if not end_label_token or end_label_token[1] != loop_label:
        raise SyntaxErrorLOL(
            f"Syntax Error on line {end_label_token[0] if end_label_token else 'EOF'}: Loop closing label '{end_label_token[1] if end_label_token else ''}' does not match starting label '{loop_label}'.")
    print_tree(f"IM OUTTA YR {end_label_token[1]}")
    advance()
    indent_level -= 1

# =========================================================
def parse_function_definition():
    global indent_level
    print_tree("<function-definition>")
    indent_level += 1

    expect("HOW IZ I")
    print_tree("HOW IZ I")

    func_token = current_token()
    if not func_token or func_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {func_token[0]}: Expected function name identifier.")
    print_tree(f"Function Name: {func_token[1]}")
    advance()

    if match("YR"):
        p_token = current_token()
        if not p_token or p_token[2] != "Identifier":
            raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
        print_tree(f"Parameter: {p_token[1]}")
        advance()

        while match("AN"):
            expect("YR", "Expected 'YR' before parameter name.")
            p_token = current_token()
            if not p_token or p_token[2] != "Identifier":
                raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
            print_tree(f"Parameter: {p_token[1]}")
            advance()

    indent_level += 1
    while current_token() and peek_lexeme() != "IF U SAY SO":
        if peek_lexeme() == "FOUND YR":
            advance()
            print_tree("FOUND YR")
            parse_expression()
        else:
            parse_statement()
    indent_level -= 1

    expect("IF U SAY SO", "Expected 'IF U SAY SO' to close function definition.")
    print_tree("IF U SAY SO")
    indent_level -= 1