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
    parse_comments()
    if pos < len(tokens):
        return tokens[pos]
    return None

def peek_lexeme():
    token = current_token()
    if token:
        return token[1]
    return None

def peek_category():
    token = current_token()
    if token:
        return token[2]
    return None

def advance():
    global pos
    token = current_token()
    pos += 1
    return token

def match(expected_lexeme):
    token = current_token()
    if token and token[1] == expected_lexeme:
        advance()
        return token
    return None

def expect(expected_lexeme, error_context=""):
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

    hai_tok = expect("HAI", "Program must start with 'HAI'.")
    print_tree("HAI")

    declarations = []
    if peek_lexeme() == "WAZZUP":
        declarations = parse_wazzup_block()

    body_statements = []
    while current_token() and peek_lexeme() != "KTHXBYE":
        stmt = parse_statement()
        if stmt:
            body_statements.append(stmt)

    expect("KTHXBYE", "Program must end with 'KTHXBYE'.")
    print_tree("KTHXBYE")

    if current_token():
        line, lexeme, _ = current_token()
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected token '{lexeme}' after KTHXBYE.")

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

    curr = current_token()
    if not curr or curr[2] != "Identifier":
        line = curr[0] if curr else "EOF"
        found = f"'{curr[1]}'" if curr else "end of file"
        raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected variable name after 'I HAS A', found {found}.")
    
    var_name = curr[1]
    print_tree(f"Identifier: {var_name}")
    advance()

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
            if peek_category() != "Data Type":
                line = current_token()[0] if current_token() else "EOF"
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected data type after 'IS NOW A'.")
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
            line = token[0]
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Unexpected identifier statement with '{lexeme}'.")
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
    
    indent_level += 1
    args = [parse_expression()]
    indent_level -= 1

    while match("+"):
        print_tree("+")
        indent_level += 1
        args.append(parse_expression())
        indent_level -= 1
        
    indent_level -= 1
    return {
        "type": "VISIBLE",
        "args": args,
        "line": vis_tok[0]
    }

# =========================================================
def parse_gimmeh():
    # <input> ::= GIMMEH <var-identifier>
    global indent_level
    print_tree("<input-statement>")
    indent_level += 1

    gim_tok = expect("GIMMEH")
    print_tree("GIMMEH")
    
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
        line, lexeme, _ = tokens[pos]
 
        if lexeme == "BTW":
            print_tree("BTW") 
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == line and tokens[pos][1] not in ["BTW", "OBTW", "TLDR"]:
                indent_level += 1
                print_tree(f"Comment: {tokens[pos][1]}")
                indent_level -= 1
                pos += 1

        elif lexeme == "OBTW":
            print_tree("OBTW")  
            pos += 1
            indent_level += 1
            while pos < len(tokens) and tokens[pos][1] != "TLDR":
                print_tree(f"Comment: {tokens[pos][1]}")
                pos += 1
            indent_level -= 1
            
            if pos < len(tokens) and tokens[pos][1] == "TLDR":
                print_tree("TLDR")  
                pos += 1
            else:
                raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'OBTW' has no closing 'TLDR'.")
        elif lexeme == "TLDR":
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: 'TLDR' found without a matching 'OBTW'.")
        else:
            break

# =========================================================
def parse_expression():
    # Parses expression nodes for literals, variables, prefix operations, typecasts, and function calls
    global indent_level
    curr = current_token()
    if not curr:
        raise SyntaxErrorLOL("Syntax Error: Unexpected end of tokens while parsing expression.")

    line, lexeme, category = curr[0], curr[1], curr[2]

    # Literals and Identifiers
    if category.startswith("Literal") or category == "Literal":
        print_tree(f"Expression ({lexeme})")
        advance()
        val_type = "YARN"
        val = lexeme
        if category == "Literal (NUMBR)":
            val_type = "NUMBR"
            val = int(lexeme)
        elif category == "Literal (NUMBAR)":
            val_type = "NUMBAR"
            val = float(lexeme)
        elif category == "Literal (TROOF)":
            val_type = "TROOF"
            val = True if lexeme == "WIN" else False
        elif category == "Literal (YARN)":
            val_type = "YARN"
            val = lexeme[1:-1] if (lexeme.startswith('"') and lexeme.endswith('"')) else lexeme
        elif category == "Literal (TYPE)":
            val_type = "TYPE"
            val = lexeme

        return {
            "type": "LITERAL",
            "val_type": val_type,
            "value": val,
            "line": line
        }

    if category == "Identifier":
        print_tree(f"Expression ({lexeme})")
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
        expect("AN", f"Expected 'AN' separator in {op_name} comparison.")
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
        if peek_category() != "Data Type":
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected valid data type in MAEK casting.")
        dt_tok = current_token()
        print_tree(f"Data Type: {dt_tok[1]}")
        advance()
        indent_level -= 1
        return {
            "type": "MAEK",
            "expr": expr,
            "target_type": dt_tok[1],
            "line": line
        }

    # Function Call
    if lexeme == "I IZ":
        print_tree("Function Call")
        advance()
        curr_id = current_token()
        if not curr_id or curr_id[2] != "Identifier":
            raise SyntaxErrorLOL(f"Syntax Error on line {line}: Expected function name after 'I IZ'.")
        func_name = curr_id[1]
        print_tree(f"Function Name: {func_name}")
        advance()
        
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

        expect("MKAY", "Expected 'MKAY' at end of function call.")
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
    global indent_level
    print_tree("<if-statement>")
    indent_level += 1

    if_tok = expect("O RLY?")
    print_tree("O RLY?")
    expect("YA RLY", "Expected 'YA RLY' after 'O RLY?'.")
    print_tree("YA RLY")

    then_block = []
    indent_level += 1
    while current_token() and peek_lexeme() not in ["MEBBE", "NO WAI", "OIC"]:
        stmt = parse_statement()
        if stmt:
            then_block.append(stmt)
    indent_level -= 1

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
    global indent_level
    print_tree("<switch-statement>")
    indent_level += 1

    sw_tok = expect("WTF?")
    print_tree("WTF?")

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
    global indent_level
    print_tree("<loop-statement>")
    indent_level += 1

    loop_tok = expect("IM IN YR")
    print_tree("IM IN YR")
    
    loop_label_token = current_token()
    if not loop_label_token or loop_label_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {loop_label_token[0]}: Expected loop label identifier.")

    loop_label = loop_label_token[1]
    print_tree(f"Label: {loop_label}")
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
    var_name = var_token[1]
    print_tree(f"Loop Var: {var_name}")
    advance()

    cond_type = peek_lexeme()
    if cond_type not in ["TIL", "WILE"]:
        raise SyntaxErrorLOL(f"Syntax Error on line {var_token[0]}: Expected 'TIL' or 'WILE' loop condition.")
    print_tree(f"Condition: {cond_type}")
    advance()
    
    indent_level += 1
    cond_expr = parse_expression()
    
    body = []
    while current_token() and peek_lexeme() != "IM OUTTA YR":
        stmt = parse_statement()
        if stmt:
            body.append(stmt)
    indent_level -= 1

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
    global indent_level
    print_tree("<function-definition>")
    indent_level += 1

    fn_tok = expect("HOW IZ I")
    print_tree("HOW IZ I")

    func_token = current_token()
    if not func_token or func_token[2] != "Identifier":
        raise SyntaxErrorLOL(f"Syntax Error on line {func_token[0]}: Expected function name identifier.")
    func_name = func_token[1]
    print_tree(f"Function Name: {func_name}")
    advance()

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