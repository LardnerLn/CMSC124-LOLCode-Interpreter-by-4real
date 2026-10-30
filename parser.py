class SyntaxErrorLOL(Exception):
    #Custom exception for syntax errors with line numbers.
    pass


# Global parser state
tokens = []
pos = 0



# Helper functions for token stream navigation
def current_token():
    #Returns the token tuple at the current position, or None if at end of file.
    if pos < len(tokens):
        return tokens[pos]
    return None


def peek_lexeme():
    #Returns the text (lexeme) of the current token
    token = current_token()
    if token:
        return token[1]
    
    else:
        None


def peek_category():
    #Returns the classification category of the current token
    token = current_token()
    
    if token:
        return token[2]
    
    else:
        None


def advance():
    #Moves the pointer forward by one token.
    global pos
    token = current_token()
    pos += 1
    
    return token


def match(expected_lexeme):
    #Advances and returns the token if it matches the expected lexeme.
    token = current_token()
    if token and token[1] == expected_lexeme:
        advance()
    
        return token
    
    return None


def expect(expected_lexeme, error_context=""):
    #Enforces that the current token is equal to expected_lexeme, or throws SyntaxErrorLOL
    token = match(expected_lexeme)
    if not token:
        curr = current_token()
        
        if curr:
            line, lexeme, _ = curr
        
            raise SyntaxErrorLOL(
                f"Syntax Error on line {line}: Expected '{expected_lexeme}', but found '{lexeme}'. {error_context}"
            )
        
        else:
        
            raise SyntaxErrorLOL(
                f"Syntax Error at end of file: Expected '{expected_lexeme}'. {error_context}"
            )
    return token




def parse(token_list):
    #Initializes global token state and starts top level parsing
    global tokens, pos
    tokens = token_list
    pos = 0
    return parse_program()



def parse_program():
    #<program> ::= HAI <wazzup-sec> <statement-block> KTHXBYE
    expect("HAI", "Program must start with 'HAI'.")

    # Optional WAZZUP block
    if peek_lexeme() == "WAZZUP":
        parse_wazzup_block()

    # Parse main body statements until KTHXBYE
    while current_token() and peek_lexeme() != "KTHXBYE":
        parse_statement()

    expect("KTHXBYE", "Program must end with 'KTHXBYE'.")

    if current_token():
        line, lexeme, _ = current_token()

        # raise is used to trigger an exception (an error) intentionally/manually
        # raise acts as an immediate shortcut that stops parsing the moment an invalid token is hit, 
        # jumping straight back to try/except block in main.py with the error message

        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected token '{lexeme}' after KTHXBYE.")

    return True


def parse_wazzup_block():
    #<wazzup-sec> ::= WAZZUP <var-declaration>* BUHBYE
    expect("WAZZUP", "Expected 'WAZZUP' to start variable declaration section.")

    while current_token() and peek_lexeme() != "BUHBYE":
        parse_var_declaration()

    expect("BUHBYE", "Expected 'BUHBYE' to close variable declaration section.")


def parse_var_declaration():
    #<var-declaration> ::= I HAS A <var-identifier> [ITZ <expr>]
    expect("I HAS A", "Variable declaration must start with 'I HAS A'.")

    curr = current_token()
    
    if not curr or curr[2] != "Identifier":
    
        line = curr[0] if curr else "EOF"
        found = f"'{curr[1]}'" if curr else "end of file"
    
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected variable name after 'I HAS A', found {found}.")

    advance()  # consume variable identifier

    if match("ITZ"):
        parse_expression()


def parse_statement():
    #Parses individual statements based on key tokens
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
    
        # Check if assignment (var R expr) or re-casting (var IS NOW A type)
        advance()
        next_lexeme = peek_lexeme()
    
        if next_lexeme == "R":
            match("R")
            parse_expression()
    
        elif next_lexeme == "IS NOW A":
            match("IS NOW A")
    
            if peek_category() != "Data Type":
                line = current_token()[0] if current_token() else "EOF"
    
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected data type after 'IS NOW A'.")
            advance()
    
        else:
            line = token[0]
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected identifier statement with '{lexeme}'.")
    else:
        # Standalone expression statement (result saved in IT)
        parse_expression()


def parse_visible():
    
    #<print> ::= VISIBLE <expr> (+ <expr>)*
    expect("VISIBLE")
    parse_expression()

    while match("+"):
        parse_expression()


def parse_gimmeh():
    
    #<input> ::= GIMMEH <var-identifier>
    expect("GIMMEH")
    curr = current_token()
    
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'GIMMEH' requires a variable identifier.")
    
    advance()


def parse_expression():
    
    #Parses prefix operations, literals, identifiers, typecasts, and function calls
    curr = current_token()
    if not curr:
        raise SyntaxErrorLOL("Syntax Error: Unexpected end of tokens while parsing expression.")

    lexeme, category = curr[1], curr[2]

    # 1. Literals and Identifiers
    if category in ["Literal", "Literal (NUMBR)", "Literal (NUMBAR)", "Literal (YARN)", "Literal (TROOF)", "Identifier"]:
        advance()
        return

    # 2. Arithmetic Operations (Binary Prefix)
    if lexeme in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]:
        advance()
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        parse_expression()
        return

    # 3. Boolean Operations
    if lexeme in ["BOTH OF", "EITHER OF", "WON OF"]:
        advance()
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        parse_expression()
        return

    if lexeme == "NOT":
        advance()
        parse_expression()
        return

    if lexeme in ["ALL OF", "ANY OF"]:
        advance()
        parse_expression()
        expect("AN", f"Expected 'AN' in {lexeme} clause.")
        parse_expression()
        while match("AN"):
            parse_expression()
        expect("MKAY", f"Expected 'MKAY' to close {lexeme} expression.")
        return

    # 4. Comparison Operations
    if lexeme in ["BOTH SAEM", "DIFFRINT"]:
        advance()
        parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} comparison.")
        parse_expression()
        return

    # 5. String Concatenation
    if lexeme == "SMOOSH":
        advance()
        parse_expression()
        expect("AN", "Expected 'AN' after first SMOOSH operand.")
        parse_expression()
        while match("AN"):
            parse_expression()
        return

    # 6. Typecasting
    if lexeme == "MAEK":
        advance()
        parse_expression()
        expect("A", "Expected 'A' after expression in MAEK typecast.")
        if peek_category() != "Data Type":
            raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Expected valid data type in MAEK casting.")
        advance()
        return

    # 7. Function Call
    if lexeme == "I IZ":
        advance()
        curr_id = current_token()
        
        if not curr_id or curr_id[2] != "Identifier":
            raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Expected function name after 'I IZ'.")
        
        advance()
        
        if match("YR"):
        
            parse_expression()
            while match("AN") and match("YR"):
                parse_expression()
        
        expect("MKAY", "Expected 'MKAY' at end of function call.")
        
        return

    raise SyntaxErrorLOL(f"Syntax Error on line {curr[0]}: Invalid expression starting with '{lexeme}'.")


def parse_if_statement():
    
    #<if-statement> ::= O RLY? YA RLY <block> [MEBBE <expr> <block>]* [NO WAI <block>] OIC
    expect("O RLY?")
    expect("YA RLY", "Expected 'YA RLY' after 'O RLY?'.")

    while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
        parse_statement()

    while peek_lexeme() == "MEBBE":
        advance()
        parse_expression()
        while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
            parse_statement()

    if match("NO WAI"):
        while current_token() and peek_lexeme() != "OIC":
            parse_statement()

    expect("OIC", "Expected 'OIC' to close conditional statement.")


def parse_switch_statement():
    #<switch-case> ::= WTF? (OMG <literal> <block>)* [OMGWTF <block>] OIC
    expect("WTF?")

    while peek_lexeme() == "OMG":
        advance()
        parse_expression()  # case literal value
        
        while current_token() and peek_lexeme() not in ["OMG", "OMGWTF", "OIC"]:
        
            if peek_lexeme() == "GTFO":
                advance()
        
            else:
                parse_statement()

    if match("OMGWTF"):
        
        while current_token() and peek_lexeme() != "OIC":
        
            if peek_lexeme() == "GTFO":
                advance()
        
            else:
                parse_statement()

    expect("OIC", "Expected 'OIC' to close switch-case statement.")


def parse_loop_statement():
    #<loop> ::= IM IN YR <label> (UPPIN|NERFIN) YR <var> (TIL|WILE) <expr> <block> IM OUTTA YR <label>
    expect("IM IN YR")

    loop_label_token = current_token()
    
    if not loop_label_token or loop_label_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected loop label identifier.")
    
    loop_label = loop_label_token[1]
    advance()

    op = peek_lexeme()
    
    if op not in ["UPPIN", "NERFIN"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected 'UPPIN' or 'NERFIN' in loop operation.")
    
    advance()

    expect("YR", "Expected 'YR' after loop operation.")

    var_token = current_token()
    
    if not var_token or var_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected variable identifier in loop operation.")
    
    advance()

    cond = peek_lexeme()
    
    if cond not in ["TIL", "WILE"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected 'TIL' or 'WILE' loop condition.")
    
    advance()
    
    parse_expression()

    while current_token() and peek_lexeme() != "IM OUTTA YR":
        parse_statement()

    expect("IM OUTTA YR", "Expected 'IM OUTTA YR' to end loop.")
    
    end_label_token = current_token()
    
    if not end_label_token or end_label_token[1] != loop_label:
    
        raise SyntaxErrorLOL(
            f"Syntax Error on line {end_label_token[0] if end_label_token else 'EOF'}: Loop closing label '{end_label_token[1] if end_label_token else ''}' does not match starting label '{loop_label}'."
        )
    
    advance()


def parse_function_definition():
    #<function> ::= HOW IZ I <func> [YR <p1> [AN YR <p2>]*] <block> IF U SAY SO[cite: 4, 20]
    expect("HOW IZ I")

    func_token = current_token()
    if not func_token or func_token[2] != "Identifier":
        
        raise SyntaxErrorLOL(f"Syntax Error on line {func_token[0]}: Expected function name identifier.")
    
    advance()

    if match("YR"):
        
        p_token = current_token()
        if not p_token or p_token[2] != "Identifier":
        
            raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
        
        advance()

        while match("AN"):
        
            expect("YR", "Expected 'YR' before parameter name.")
            p_token = current_token()
        
            if not p_token or p_token[2] != "Identifier":
                raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
        
            advance()

    while current_token() and peek_lexeme() != "IF U SAY SO":
        
        if peek_lexeme() == "FOUND YR":
            advance()
            parse_expression()
        
        else:
            parse_statement()

    expect("IF U SAY SO", "Expected 'IF U SAY SO' to close function definition.")