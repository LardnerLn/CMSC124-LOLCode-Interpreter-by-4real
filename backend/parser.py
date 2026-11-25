# parser.py
# Syntax Analyzer and AST Builder for LOLCODE Interpreter

class SyntaxErrorLOL(Exception):
    # Custom exception for syntax errors with line numbers
    pass

indent_level = 0

def print_tree(node_name):
    # Displays hierarchical parse tree formatting
    global indent_level
    prefix = "│   " * indent_level + "├── "
    print(f"{prefix}{node_name}")

# Global parser state
tokens = []
pos = 0

# =========================================================
# Helper functions for token stream navigation
def current_token():
    # Skip comments first before checking current token
    parse_comments()
    if pos < len(tokens):
        return tokens[pos]
    return None

# ========================
def peek_lexeme():
    # Look at the text of the current token
    token = current_token()
    if token:
        return token[1]
    return None

# ========================
def peek_category():
    # Look at the category of the current token
    token = current_token()
    if token:
        return token[2]
    return None

# ========================
def advance():
    # Move to the next token and return the current one
    global pos
    token = current_token()
    pos += 1
    return token

# ========================
def match(expected_lexeme):
    # Consume token only if it matches what we expect
    token = current_token()
    if token and token[1] == expected_lexeme:
        advance()
        return token
    return None

# ========================
def expect(expected_lexeme, error_context=""):
    # Require a specific token or raise a syntax error
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
     # Initializes parser state, prints the parse tree, and returns the AST
    global tokens, pos, indent_level
    tokens = token_list
    pos = 0
    indent_level = 0
    
    print("\n================ PARSE TREE / GRAMMAR STRUCTURE ================")
    ast = parse_program()
    print("================================================================")
    return ast

# =========================================================
def parse_program():
    # <program> ::= HAI <wazzup-sec> <statement-block> KTHXBYE
    global indent_level
    print_tree("<program>")
    indent_level += 1

    functions = []
    # Allow top-level functions declared before HAI
    while current_token() and peek_lexeme() == "HOW IZ I":
        functions.append(parse_function_definition())

    hai_tok = expect("HAI", "Program must include 'HAI'.")
    print_tree("HAI")

    declarations = []
    # Parse optional WAZZUP variable block if present
    if current_token() and peek_lexeme() == "WAZZUP":
        declarations = parse_wazzup_block()

    # Collect statements until the program ends with KTHXBYE
    body_statements = list(functions)
    while current_token() and peek_lexeme() != "KTHXBYE":
        stmt = parse_statement()
        if stmt:
            body_statements.append(stmt)

    expect("KTHXBYE", "Program must end with 'KTHXBYE'.")
    print_tree("KTHXBYE")

    # After KTHXBYE, only comments
    # parse_comments()) and function definitions are valid
    while current_token():
        if peek_lexeme() == "HOW IZ I":
            body_statements.append(parse_function_definition())
        else:
            curr = current_token()
            line = curr[0] if curr else "EOF"
            found = curr[1] if curr else "EOF"
            raise SyntaxErrorLOL(
                f"Syntax Error on line {line}: Unexpected '{found}' after 'KTHXBYE'. "
                "Only comments and function definitions ('HOW IZ I') are allowed after 'KTHXBYE'."
            )

    indent_level -= 1

    return {
        "type": "PROGRAM",
        "declarations": declarations,
        "body": body_statements,
        "line": hai_tok[0]
    }
# =========================================================
def parse_wazzup_block():
    # <wazzup-sec> ::= WAZZUP <var-declaration>* BUHBYE
    global indent_level
    print_tree("<wazzup-sec>")
    indent_level += 1

    expect("WAZZUP", "Expected 'WAZZUP' to start variable declaration section.")
    print_tree("WAZZUP")

    # Read every variable declaration until BUHBYE
    declarations = []
    while current_token() and peek_lexeme() != "BUHBYE":
        decl = parse_var_declaration()
        declarations.append(decl)

    expect("BUHBYE", "Expected 'BUHBYE' to close variable declaration section.")
    print_tree("BUHBYE")
    indent_level -= 1
    return declarations

# =========================================================
def parse_var_declaration():
    # <var-declaration> ::= I HAS A <var-identifier> [ITZ <expr>]
    global indent_level
    print_tree("<var-declaration>")
    indent_level += 1

    has_tok = expect("I HAS A", "Variable declaration must start with 'I HAS A'.")
    print_tree("I HAS A")

    # Make sure a valid variable name comes next
    curr = current_token()
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        found = f"'{curr[1]}'" if curr else "end of file"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected variable name after 'I HAS A', found {found}.")
    
    var_name = curr[1]
    print_tree(f"Identifier: {var_name}")
    advance()

    # Optional starting value with ITZ
    init_expr = None
    if match("ITZ"):
        print_tree("ITZ")
        indent_level += 1
        init_expr = parse_expression()
        indent_level -= 1

    indent_level -= 1
    return {
        "type": "VAR_DECL",
        "name": var_name,
        "init": init_expr,
        "line": has_tok[0]
    }

# =========================================================
def parse_statement():
    # Parses individual statements and constructs statement AST nodes
    token = current_token()
    if not token:
        return None

    lexeme = token[1]

    # Route statement based on starting keyword
    if lexeme == "VISIBLE":
        return parse_visible()
    elif lexeme == "GIMMEH":
        return parse_gimmeh()
    elif lexeme == "O RLY?":
        return parse_if_statement()
    elif lexeme == "WTF?":
        return parse_switch_statement()
    elif lexeme == "IM IN YR":
        return parse_loop_statement()
    elif lexeme == "HOW IZ I":
        return parse_function_definition()
    elif token[2] == "Identifier":
        # Handle variable reassignment, type recast, or standalone variable
        global indent_level
        print_tree("<assignment>")
        indent_level += 1
        
        var_tok = advance()
        print_tree(f"Identifier: {var_tok[1]}")
        next_lexeme = peek_lexeme()

        if next_lexeme == "R":
            match("R")
            print_tree("R")
            indent_level += 1
            val_expr = parse_expression()
            indent_level -= 1
            indent_level -= 1
            return {
                "type": "ASSIGN",
                "name": var_tok[1],
                "expr": val_expr,
                "line": var_tok[0]
            }
        elif next_lexeme == "IS NOW A":
            match("IS NOW A")
            print_tree("IS NOW A")
            dt_tok = advance()
            print_tree(f"Data Type: {dt_tok[1]}")
            indent_level -= 1
            return {
                "type": "RECAST",
                "name": var_tok[1],
                "target_type": dt_tok[1],
                "line": var_tok[0]
            }
        else:
            indent_level -= 1
            return {
                "type": "EXPR_STMT",
                "expr": {
                    "type": "VARIABLE",
                    "name": var_tok[1],
                    "line": var_tok[0]
                },
                "line": var_tok[0]
            }
    else:
        # Standalone expression statement (saves output into IT)
        expr_node = parse_expression()
        return {
            "type": "EXPR_STMT",
            "expr": expr_node,
            "line": expr_node["line"]
        }

# =========================================================
def parse_visible():
    # <print> ::= VISIBLE <expr> (+ <expr>)*
    global indent_level
    print_tree("<output-statement>")
    indent_level += 1

    vis_tok = expect("VISIBLE")
    print_tree("VISIBLE")
    vis_line = vis_tok[0]
    indent_level += 1

    # Parse first printed value
    args = [parse_expression()]

    # Keep reading extra items on the same VISIBLE line
    while True:
        curr = current_token()
        if not curr or curr[0] != vis_line:
            break
        if curr[1] == "+":  
                advance()  # Consume '+'
                print_tree("+")  
                args.append(parse_expression())  # Parse next VISIBLE operand
        elif curr[1] == "AN":  # Support 'AN' separator if present on same line
            advance()  # Consume 'AN'
            print_tree("AN")  
            args.append(parse_expression()) 
        else:
            break

    indent_level -= 2
    return {
        "type": "VISIBLE",
        "args": args,
        "line": vis_line
    }

# =========================================================
def parse_gimmeh():
    # <input> ::= GIMMEH <var-identifier>
    global indent_level
    print_tree("<input-statement>")
    indent_level += 1

    gim_tok = expect("GIMMEH")
    print_tree("GIMMEH")
    
    # Require a variable name to store user input
    curr = current_token()
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'GIMMEH' requires a variable identifier.")
    
    var_name = curr[1]
    print_tree(f"Identifier: {var_name}")
    advance()
    indent_level -= 1
    return {
        "type": "GIMMEH",
        "name": var_name,
        "line": gim_tok[0]
    }

# =========================================================
def parse_comments():
    # Filters comments and maintains parse tree output
    global pos, indent_level
    while pos < len(tokens):
        line, lexeme, category = tokens[pos]

        if category == "Comment Keyword" and lexeme == "BTW":
            # Single-line comment with optional text on the same line
            print_tree("BTW") 
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == line:      # rest of line is one comment token, take it as-is
                indent_level += 1   
                print_tree(f"Comment: {tokens[pos][1]}")
                indent_level -= 1
                pos += 1

        elif category == "Comment Keyword" and lexeme == "OBTW":
            if pos > 0 and tokens[pos - 1][0] == line:            # OBTW must be first on its line
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'OBTW' must be on its own line; it cannot follow a statement.")

            # Multi-line comment block until TLDR
            print_tree("OBTW")  
            pos += 1
            indent_level += 1
            while pos < len(tokens) and tokens[pos][1] != "TLDR":
                print_tree(f"Comment: {tokens[pos][1]}")
                pos += 1
            indent_level -= 1
            
            if pos < len(tokens) and tokens[pos][1] == "TLDR":
                tldr_line = tokens[pos][0]
                print_tree("TLDR")  
                pos += 1
                if pos < len(tokens) and tokens[pos][0] == tldr_line and tokens[pos][1] != "BTW":
                    raise SyntaxErrorLOL(f"Syntax Error on line {tldr_line}: 'TLDR' must be on its own line; only a BTW comment may follow it.")
            else:
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'OBTW' has no closing 'TLDR'.")
        elif category == "Comment Keyword" and lexeme == "TLDR":
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'TLDR' found without a matching 'OBTW'.")
        elif category in ["Comment Text"]:
            # Skip leftover comment text tokens
            pos += 1
        else:
            break

# =========================================================
def parse_expression():
    # Parses expression nodes for literals, variables, prefix operations, typecasts, and function calls
    global indent_level
    parse_comments()

    curr = current_token()
    if not curr:
        raise SyntaxErrorLOL("Syntax Error: Unexpected end of tokens while parsing expression.")

    line, lexeme, category = curr[0], curr[1], curr[2]

    if lexeme == "+":  # Reject '+' outside VISIBLE statements
        raise SyntaxErrorLOL( 
            f"Syntax Error on line {line}: '+' is only allowed in VISIBLE; use SMOOSH for string concatenation."  
        )
    
    # Literals
    if category.startswith("Literal") or lexeme in ["WIN", "FAIL"]:
        print_tree(f"Literal: {lexeme}")
        advance()
        val_type = "YARN"
        val = lexeme

        # Convert literal text into its matching Python type
        if "NUMBR" in category:
            val_type = "NUMBR"
            val = int(lexeme) if lexeme.lstrip("-").isdigit() else lexeme
        elif "NUMBAR" in category:
            val_type = "NUMBAR"
            val = float(lexeme) if "." in lexeme else lexeme
        elif "TROOF" in category or lexeme in ["WIN", "FAIL"]:
            val_type = "TROOF"
            val = True if lexeme == "WIN" else False
        elif "YARN" in category:
            val_type = "YARN"
            val = lexeme[1:-1] if (lexeme.startswith('"') and lexeme.endswith('"')) else lexeme
        elif "TYPE" in category:
            val_type = "TYPE"
            val = lexeme

        return {
            "type": "LITERAL",
            "val_type": val_type,
            "value": val,
            "line": line
        }
    if lexeme == '"':
            # Read quoted string pieces between opening and closing quotes
            advance()  # Opening "
            inner_val = ""
            curr_inner = current_token()
            if curr_inner and curr_inner[1] != '"':
                inner_val = curr_inner[1]
                print_tree(f"Literal: {inner_val}")
                advance()
            match('"')  # Closing "
            return {
                "type": "LITERAL",
                "val_type": "YARN",
                "value": inner_val,
                "line": line
            }
    # Identifiers
    if category == "Identifier":
        print_tree(f"Identifier: {lexeme}")
        advance()
        return {
            "type": "VARIABLE",
            "name": lexeme,
            "line": line
        }

    # Binary Arithmetic Operations
    if lexeme in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        left = parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        print_tree("AN")
        right = parse_expression()
        indent_level -= 1
        return {
            "type": "BIN_OP",
            "op": lexeme,
            "left": left,
            "right": right,
            "line": line
        }

    # Binary Boolean Operations
    if lexeme in ["BOTH OF", "EITHER OF", "WON OF"]:
        print_tree(lexeme)
        advance()
        indent_level += 1
        left = parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} expression.")
        print_tree("AN")
        right = parse_expression()
        indent_level -= 1
        return {
            "type": "BIN_OP",
            "op": lexeme,
            "left": left,
            "right": right,
            "line": line
        }

    # Unary NOT
    if lexeme == "NOT":
        print_tree("NOT")
        advance()
        indent_level += 1
        operand = parse_expression()
        indent_level -= 1
        return {
            "type": "UNARY_OP",
            "op": "NOT",
            "operand": operand,
            "line": line
        }

    # Variadic Boolean (ALL OF / ANY OF)
    if lexeme in ["ALL OF", "ANY OF"]:
        print_tree(lexeme)
        op_name = lexeme
        advance()
        indent_level += 1
        args = [parse_expression()]
        expect("AN", f"Expected 'AN' in {op_name} clause.")
        print_tree("AN")
        args.append(parse_expression())
        # Allow extra operands separated by AN until MKAY closes it
        while match("AN"):
            print_tree("AN")
            args.append(parse_expression())
        expect("MKAY", f"Expected 'MKAY' to close {op_name} expression.")
        print_tree("MKAY")
        indent_level -= 1
        return {
            "type": "VARIADIC_BOOL",
            "op": op_name,
            "args": args,
            "line": line
        }

    # Comparison Operations
    if lexeme in ["BOTH SAEM", "DIFFRINT"]:
        print_tree(lexeme)
        op_name = lexeme
        advance()
        indent_level += 1
        left = parse_expression()
        expect("AN", f"Expected 'AN' separator in {lexeme} comparison.")
        print_tree("AN")
        right = parse_expression()
        indent_level -= 1
        return {
            "type": "BIN_OP",
            "op": op_name,
            "left": left,
            "right": right,
            "line": line
        }

    # String Concatenation
    if lexeme == "SMOOSH":
        print_tree("SMOOSH")
        advance()
        indent_level += 1
        args = [parse_expression()]
        expect("AN", "Expected 'AN' after first SMOOSH operand.")
        print_tree("AN")
        args.append(parse_expression())
        # Collect any additional parts joined with AN
        while match("AN"):
            print_tree("AN")
            args.append(parse_expression())
        indent_level -= 1
        return {
            "type": "SMOOSH",
            "args": args,
            "line": line
        }

    # Typecasting (MAEK)
    if lexeme == "MAEK":
        print_tree("MAEK")
        advance()
        indent_level += 1
        expr = parse_expression()
        expect("A", "Expected 'A' after expression in MAEK typecast.")
        print_tree("A")
        curr_type = advance()
        target_type = curr_type[1]
        print_tree(f"Data Type: {target_type}")
        indent_level -= 1
        return {
            "type": "MAEK",
            "expr": expr,
            "target_type": target_type,
            "line": line
        }

    # Function Call
    if lexeme == "I IZ":
        print_tree("Function Call")
        advance()
        curr_id = current_token()
        func_name = curr_id[1]
        print_tree(f"Function Name: {func_name}")
        advance()
        
        # Parse optional arguments passed after YR
        args = []
        indent_level += 1
        if match("YR"):
            print_tree("YR")
            args.append(parse_expression())
            while match("AN"):
                expect("YR", "Expected 'YR' before parameter argument in function call.")
                print_tree("AN YR")
                args.append(parse_expression())
        indent_level -= 1

        expect("MKAY", "Expected 'MKAY' at the end of function call.")  # Require MKAY after end of func call
        print_tree("MKAY")  

        return {
            "type": "FUNC_CALL",
            "name": func_name,
            "args": args,
            "line": line
        }

    raise SyntaxErrorLOL(f"Syntax Error on line {line}: Invalid expression starting with '{lexeme}'.")

# =========================================================
def parse_if_statement():
    # Parse O RLY? conditional block with YA RLY, MEBBE, and NO WAI
    global indent_level
    print_tree("<if-statement>")
    indent_level += 1

    if_tok = expect("O RLY?")
    print_tree("O RLY?")
    expect("YA RLY", "Expected 'YA RLY' after 'O RLY?'.")
    print_tree("YA RLY")

    # Main true branch statements
    then_block = []
    indent_level += 1
    while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
        stmt = parse_statement()
        if stmt:
            then_block.append(stmt)
    indent_level -= 1

    # Optional else-if branches
    mebbe_blocks = []
    while peek_lexeme() == "MEBBE":
        advance()
        print_tree("MEBBE")
        indent_level += 1
        cond_expr = parse_expression()
        m_block = []
        while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
            stmt = parse_statement()
            if stmt:
                m_block.append(stmt)
        mebbe_blocks.append((cond_expr, m_block))
        indent_level -= 1

    # Optional fallback else branch
    else_block = []
    if match("NO WAI"):
        print_tree("NO WAI")
        indent_level += 1
        while current_token() and peek_lexeme() != "OIC":
            stmt = parse_statement()
            if stmt:
                else_block.append(stmt)
        indent_level -= 1

    expect("OIC", "Expected 'OIC' to close conditional statement.")
    print_tree("OIC")
    indent_level -= 1
    return {
        "type": "IF_STMT",
        "then_block": then_block,
        "mebbe_blocks": mebbe_blocks,
        "else_block": else_block,
        "line": if_tok[0]
    }

# =========================================================
def parse_switch_statement():
    # Parse WTF? switch block with OMG cases and optional OMGWTF default
    global indent_level
    print_tree("<switch-statement>")
    indent_level += 1

    sw_tok = expect("WTF?")
    print_tree("WTF?")

    # Collect each OMG case and its statements
    cases = []
    while peek_lexeme() == "OMG":
        advance()
        print_tree("OMG Case")
        indent_level += 1
        case_val = parse_expression()
        case_block = []
        while current_token() and peek_lexeme() not in ["OMG", "OMGWTF", "OIC"]:
            if peek_lexeme() == "GTFO":
                gtfo_tok = advance()
                print_tree("GTFO")
                case_block.append({"type": "GTFO", "line": gtfo_tok[0]})
            else:
                stmt = parse_statement()
                if stmt:
                    case_block.append(stmt)
        cases.append((case_val, case_block))
        indent_level -= 1

    # Optional default branch when no case matches
    default_block = []
    if match("OMGWTF"):
        print_tree("OMGWTF Default")
        indent_level += 1
        while current_token() and peek_lexeme() != "OIC":
            if peek_lexeme() == "GTFO":
                gtfo_tok = advance()
                print_tree("GTFO")
                default_block.append({"type": "GTFO", "line": gtfo_tok[0]})
            else:
                stmt = parse_statement()
                if stmt:
                    default_block.append(stmt)
        indent_level -= 1

    expect("OIC", "Expected 'OIC' to close switch-case statement.")
    print_tree("OIC")
    indent_level -= 1
    return {
        "type": "SWITCH_STMT",
        "cases": cases,
        "default_block": default_block,
        "line": sw_tok[0]
    }

# =========================================================
def parse_loop_statement():
    # Parse IM IN YR loop header, condition, body, and matching end label
    global indent_level
    print_tree("<loop-statement>")
    indent_level += 1

    loop_tok = expect("IM IN YR")
    print_tree("IM IN YR")
    
    # Read loop label name
    loop_label_token = current_token()
    if not loop_label_token or loop_label_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected loop label identifier.")

    loop_label = loop_label_token[1]
    print_tree(f"Label: {loop_label}")
    advance()

    # Check whether loop counts up or down
    op = peek_lexeme()
    if op not in ["UPPIN", "NERFIN"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected 'UPPIN' or 'NERFIN' in loop operation.")
    print_tree(f"Operation: {op}")
    advance()

    # Read loop counter variable after YR
    expect("YR", "Expected 'YR' after loop operation.")
    var_token = current_token()
    if not var_token or var_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected variable identifier in loop operation.")
    var_name = var_token[1]
    print_tree(f"Loop Var: {var_name}")
    advance()

    # Read TIL or WILE stop condition
    cond_type = peek_lexeme()
    if cond_type not in ["TIL", "WILE"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected 'TIL' or 'WILE' loop condition.")
    print_tree(f"Condition: {cond_type}")
    advance()
    
    indent_level += 1
    cond_expr = parse_expression()
    
    # Parse statements inside the loop body
    body = []
    while current_token() and peek_lexeme() != "IM OUTTA YR":
        stmt = parse_statement()
        if stmt:
            body.append(stmt)
    indent_level -= 1

    # Match closing IM OUTTA YR label with opening label
    expect("IM OUTTA YR", "Expected 'IM OUTTA YR' to end loop.")
    end_label_token = current_token()
    if not end_label_token or end_label_token[1] != loop_label:
        raise SyntaxErrorLOL(
            f"Syntax Error on line {end_label_token[0] if end_label_token else 'EOF'}: Loop closing label '{end_label_token[1] if end_label_token else ''}' does not match starting label '{loop_label}'.")
    print_tree(f"IM OUTTA YR {end_label_token[1]}")
    advance()
    indent_level -= 1
    return {
        "type": "LOOP_STMT",
        "label": loop_label,
        "operation": op,
        "var_name": var_name,
        "cond_type": cond_type,
        "cond_expr": cond_expr,
        "body": body,
        "line": loop_tok[0]
    }

# =========================================================
def parse_function_definition():
    # Parse HOW IZ I function name, parameters, body, and IF U SAY SO
    global indent_level
    print_tree("<function-definition>")
    indent_level += 1

    fn_tok = expect("HOW IZ I")
    print_tree("HOW IZ I")

    # Read function name
    func_token = current_token()
    if not func_token or func_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {func_token[0]}: Expected function name identifier.")
    func_name = func_token[1]
    print_tree(f"Function Name: {func_name}")
    advance()

    # Collect optional parameter names after YR and AN YR
    params = []
    if match("YR"):
        p_token = current_token()
        if not p_token or p_token[2] != "Identifier":
            raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
        params.append(p_token[1])
        print_tree(f"Parameter: {p_token[1]}")
        advance()

        while match("AN"):
            expect("YR", "Expected 'YR' before parameter name.")
            p_token = current_token()
            if not p_token or p_token[2] != "Identifier":
                raise SyntaxErrorLOL(f"Syntax Error on line {p_token[0]}: Expected parameter identifier.")
            params.append(p_token[1])
            print_tree(f"Parameter: {p_token[1]}")
            advance()

    # Parse function body statements, including FOUND YR and GTFO
    body = []
    indent_level += 1
    while current_token() and peek_lexeme() != "IF U SAY SO":
        if peek_lexeme() == "FOUND YR":
            ret_tok = advance()
            print_tree("FOUND YR")
            ret_expr = parse_expression()
            body.append({
                "type": "RETURN",
                "expr": ret_expr,
                "line": ret_tok[0]
            })
        elif peek_lexeme() == "GTFO":
            gtfo_tok = advance()
            print_tree("GTFO")
            body.append({"type": "GTFO", "line": gtfo_tok[0]})
        else:
            stmt = parse_statement()
            if stmt:
                body.append(stmt)
    indent_level -= 1

    expect("IF U SAY SO", "Expected 'IF U SAY SO' to close function definition.")
    print_tree("IF U SAY SO")
    indent_level -= 1
    return {
        "type": "FUNC_DEF",
        "name": func_name,
        "params": params,
        "body": body,
        "line": fn_tok[0]
    }