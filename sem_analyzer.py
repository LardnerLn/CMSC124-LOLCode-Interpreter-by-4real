# semantic_analyzer.py
# Semantic Analyzer for LOLCODE project using pure functions

class SemanticErrorLOL(Exception):
    # Custom exception for semantic errors
    pass

# Global storage for tracking declared variables and function signatures during analysis
declared_vars = set()
declared_functions = {}

def analyze_semantics(ast):
    # Main entry point to validate the program AST
    global declared_vars, declared_functions
    declared_vars = set(["IT"])
    declared_functions = {}

    if not ast or ast.get("type") != "PROGRAM":
        raise SemanticErrorLOL("Semantic Error: Invalid AST structure.")

    # Phase 1: Validate variable declarations inside the WAZZUP block
    declarations = ast.get("declarations", [])
    for decl in declarations:
        analyze_var_decl(decl)

    # Phase 2: Validate body statements
    body_statements = ast.get("body", [])
    for stmt in body_statements:
        analyze_statement(stmt, local_scope=None)

def analyze_var_decl(decl):
    # Validates a single variable declaration
    global declared_vars
    line = decl.get("line", "Unknown")
    var_name = decl.get("name")

    if var_name in declared_vars:
        raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Variable '" + str(var_name) + "' is already declared.")

    declared_vars.add(var_name)

    # Check initial value expression if present
    init_expr = decl.get("init")
    if init_expr:
        analyze_expression(init_expr, local_scope=None)

def analyze_statement(stmt, local_scope=None):
    # Checks statement types and validates child expressions or sub-blocks
    if not stmt:
        return

    stmt_type = stmt.get("type")
    line = stmt.get("line", "Unknown")

    if stmt_type == "ASSIGN":
        var_name = stmt.get("name")
        check_variable_declared(var_name, line, local_scope)
        analyze_expression(stmt.get("expr"), local_scope)

    elif stmt_type == "RECAST":
        var_name = stmt.get("name")
        check_variable_declared(var_name, line, local_scope)

    elif stmt_type == "VISIBLE":
        for arg in stmt.get("args", []):
            analyze_expression(arg, local_scope)

    elif stmt_type == "GIMMEH":
        var_name = stmt.get("name")
        check_variable_declared(var_name, line, local_scope)

    elif stmt_type == "EXPR_STMT":
        analyze_expression(stmt.get("expr"), local_scope)

    elif stmt_type == "IF_STMT":
        for stmt_in_then in stmt.get("then_block", []):
            analyze_statement(stmt_in_then, local_scope)

        for mebbe_expr, mebbe_block in stmt.get("mebbe_blocks", []):
            analyze_expression(mebbe_expr, local_scope)
            for stmt_in_m in mebbe_block:
                analyze_statement(stmt_in_m, local_scope)

        for stmt_in_else in stmt.get("else_block", []):
            analyze_statement(stmt_in_else, local_scope)

    elif stmt_type == "SWITCH_STMT":
        for case_val_node, case_block in stmt.get("cases", []):
            analyze_expression(case_val_node, local_scope)
            for stmt_in_c in case_block:
                analyze_statement(stmt_in_c, local_scope)

        for stmt_in_d in stmt.get("default_block", []):
            analyze_statement(stmt_in_d, local_scope)

    elif stmt_type == "LOOP_STMT":
        var_name = stmt.get("var_name")
        check_variable_declared(var_name, line, local_scope)
        analyze_expression(stmt.get("cond_expr"), local_scope)
        for stmt_in_loop in stmt.get("body", []):
            analyze_statement(stmt_in_loop, local_scope)

    elif stmt_type == "FUNC_DEF":
        func_name = stmt.get("name")
        params = stmt.get("params", [])

        if func_name in declared_functions:
            raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Function '" + str(func_name) + "' is already defined.")

        declared_functions[func_name] = len(params)

        # Create isolated parameter scope for function body
        func_scope = set(["IT"])
        for param in params:
            func_scope.add(param)

        for stmt_in_fn in stmt.get("body", []):
            analyze_statement(stmt_in_fn, local_scope=func_scope)

    elif stmt_type == "RETURN":
        analyze_expression(stmt.get("expr"), local_scope)

    elif stmt_type == "GTFO":
        pass

def analyze_expression(expr, local_scope=None):
    # Checks expressions for valid variables, operators, and functions
    if not expr:
        return

    expr_type = expr.get("type")
    line = expr.get("line", "Unknown")

    if expr_type == "LITERAL":
        pass

    elif expr_type == "VARIABLE":
        var_name = expr.get("name")
        check_variable_declared(var_name, line, local_scope)

    elif expr_type == "BIN_OP":
        left = expr.get("left")
        right = expr.get("right")
        op = expr.get("op")

        analyze_expression(left, local_scope)
        analyze_expression(right, local_scope)

        # Check for division/modulo by literal zero
        if op in ["QUOSHUNT OF", "MOD OF"]:
            if right.get("type") == "LITERAL" and right.get("value") in [0, 0.0, "0", "0.0"]:
                raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Division or modulo by zero detected.")

    elif expr_type == "UNARY_OP":
        analyze_expression(expr.get("operand"), local_scope)

    elif expr_type == "VARIADIC_BOOL":
        for arg in expr.get("args", []):
            analyze_expression(arg, local_scope)

    elif expr_type == "SMOOSH":
        for arg in expr.get("args", []):
            analyze_expression(arg, local_scope)

    elif expr_type == "MAEK":
        analyze_expression(expr.get("expr"), local_scope)

    elif expr_type == "FUNC_CALL":
        func_name = expr.get("name")
        args = expr.get("args", [])

        if func_name not in declared_functions:
            raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Call to undefined function '" + str(func_name) + "'.")

        expected_count = declared_functions[func_name]
        if len(args) != expected_count:
            raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Function '" + str(func_name) + "' expects " + str(expected_count) + " arguments, got " + str(len(args)) + ".")

        for arg in args:
            analyze_expression(arg, local_scope)

def check_variable_declared(name, line, local_scope=None):
    # Verifies that a variable is declared in either local or global scope
    if local_scope is not None:
        if name in local_scope:
            return
        else:
            raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Variable '" + str(name) + "' is not accessible in this scope.")

    if name not in declared_vars:
        raise SemanticErrorLOL("Semantic Error on line " + str(line) + ": Variable '" + str(name) + "' used before declaration.")