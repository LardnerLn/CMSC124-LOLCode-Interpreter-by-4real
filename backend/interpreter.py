# interpreter.py

import re
from backend.symbol_table import create_symbol_table, declare_var, assign_var, get_var_value

# Exception for runtime errors
class InterpreterRuntimeError(Exception):
    pass

# Global storage for functions and io 
my_functions = {}
print_func = print
input_func = input
update_table_func = None

def notify_symbol_table(symbol_table):
    # Send a copy of the symbol table to the GUI whenever a variable changes
    if update_table_func is not None:
        update_table_func(dict(symbol_table))

def raise_my_error(msg, node=None):
    # Raise error with line info
    if node is not None and "line" in node and node["line"] is not None:
        raise InterpreterRuntimeError("Error on line " + str(node["line"]) + ": " + msg)
    raise InterpreterRuntimeError("Runtime Error: " + msg)


# =========================================================
# TYPECASTING SECTION
# =========================================================
def get_data_type(val):
    # Get value data type
    if val is None:
        return "NOOB"
    if isinstance(val, bool):
        return "TROOF"
    if isinstance(val, int):
        return "NUMBR"
    if isinstance(val, float):
        return "NUMBAR"
    return "YARN"

# ========================================
def to_bool(val):
    # Convert value to bool
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        # Zero is false, non-zero is true
        if val == 0:
            return False
        else:
            return True
    if val == "":
        return False
    return True

# ========================================
def to_num(val, node):
    # Convert value to number
    if val is None:
        raise_my_error("Noob cant be number", node)
    if isinstance(val, bool):
        # True becomes 1 and false becomes 0
        if val == True:
            return 1
        else:
            return 0
    if isinstance(val, (int, float)):
        return val

    # Parse string to number
    s = str(val).strip()
    if s == "":  # Handle empty string inputs as 0
        return 0
    # Check whole numbers first, then decimals
    if re.match(r'^-?[0-9]+$', s):
        return int(s)
    if re.match(r'^-?[0-9]+\.[0-9]+$', s):
        return float(s)
        
    raise_my_error("Cannot parse number: " + str(val), node)

# ========================================
def to_string(val, node, explicit=False):
    # Convert value to yarn safely
    if val is None:
        return "NOOB"
    if isinstance(val, bool):
        if val == True:
            return "WIN"
        else:
            return "FAIL"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        # Format decimals to two places
        return f"{val:.2f}"
    return str(val)

# ========================================
def do_cast(val, target, node):
    # Cast value to target
    if target == "TROOF":
        return to_bool(val)
    elif target == "NOOB":
        return None
    elif target == "YARN":
        return to_string(val, node, explicit=True)
    elif target == "NUMBR":
        if val is None:
            return 0
        num = to_num(val, node)
        # Cut off decimal part for whole numbers
        return int(num)
    elif target == "NUMBAR":
        if val is None:
            return 0.0
        num = to_num(val, node)
        return float(num)
    else:
        raise_my_error("Unknown type: " + str(target), node)

# ========================================
def check_equals(a, b):
    # Compare values safely
    t1 = get_data_type(a)
    t2 = get_data_type(b)
    # Compare ints and floats directly
    if t1 in ["NUMBR", "NUMBAR"] and t2 in ["NUMBR", "NUMBAR"]:
        return a == b
    if t1 != t2:
        return False
    return a == b


# =========================================================
# EXPRESSIONS SECTION
# =========================================================
def eval_expression(expr, symbol_table):
    # Evaluate expression node
    etype = expr["type"]

    if etype == "LITERAL":
        return expr["value"]
    elif etype == "VARIABLE":
        try: 
            return get_var_value(symbol_table, expr["name"]) 
        except Exception as e: 
            raise_my_error(str(e), expr) 
    elif etype == "BIN_OP":
        return eval_binary_op(expr, symbol_table)
    elif etype == "UNARY_OP":
        # Flip boolean value for NOT
        val = eval_expression(expr["operand"], symbol_table)
        return not to_bool(val)
    elif etype == "VARIADIC_BOOL":
        results = []
        for arg in expr["args"]:
            results.append(to_bool(eval_expression(arg, symbol_table)))
            
        if expr["op"] == "ALL OF":
            # Stop early if any item is false
            all_true = True
            for r in results:
                if not r:
                    all_true = False
                    break
            return all_true
        else:
            # Return true if at least one item is true
            any_true = False
            for r in results:
                if r:
                    any_true = True
                    break
            return any_true
    elif etype == "SMOOSH":
        # Combine all parts into one string
        res_str = ""
        for arg in expr["args"]:
            res_str = res_str + to_string(eval_expression(arg, symbol_table), expr)
        return res_str
    elif etype == "MAEK":
        val = eval_expression(expr["expr"], symbol_table)
        return do_cast(val, expr["target_type"], expr)
    elif etype == "FUNC_CALL":
        return call_user_func(expr, symbol_table)

    raise_my_error("Unknown expression type: " + str(etype), expr)

# ========================================
def eval_binary_op(expr, symbol_table):
    # Run math, logic, or comparison operations on two values
    op = expr["op"]
    left = eval_expression(expr["left"], symbol_table)
    right = eval_expression(expr["right"], symbol_table)

    if op == "BOTH OF":
        return to_bool(left) and to_bool(right)
    elif op == "EITHER OF":
        return to_bool(left) or to_bool(right)
    elif op == "WON OF":
        # True when one side is true and the other is false
        return to_bool(left) != to_bool(right)
    elif op == "BOTH SAEM":
        return check_equals(left, right)
    elif op == "DIFFRINT":
        return not check_equals(left, right)

    num_a = to_num(left, expr)
    num_b = to_num(right, expr)
    
    both_ints = False
    if isinstance(num_a, int) and isinstance(num_b, int):
        both_ints = True

    if op == "SUM OF":
        return num_a + num_b
    elif op == "DIFF OF":
        return num_a - num_b
    elif op == "PRODUKT OF":
        return num_a * num_b
    elif op == "QUOSHUNT OF":
        if num_b == 0:
            raise_my_error("Division by zero error", expr)
        # Use whole-number division when both values are integers
        if both_ints:
            return num_a // num_b
        return num_a / num_b
    elif op == "MOD OF":
        if num_b == 0:
            raise_my_error("Modulo zero error", expr)
        if both_ints:
            return num_a % num_b
        return num_a % num_b
    elif op == "BIGGR OF":
        return max(num_a, num_b)
    elif op == "SMALLR OF":
        return min(num_a, num_b)

    raise_my_error("Unknown operator: " + str(op), expr)

# ========================================
def call_user_func(expr, symbol_table):
    # Call a user function using its own local variables
    fname = expr["name"]
    if fname not in my_functions:
        raise_my_error("Function not found: " + str(fname), expr)

    func_node = my_functions[fname]
    params = func_node["params"]
    
    if len(expr["args"]) != len(params):
        raise_my_error("Argument count mismatch", expr)

    local_symbol_table = create_symbol_table()
    try: 
        # Pass argument values into function parameters
        for i in range(len(params)):
            declare_var(local_symbol_table, params[i], eval_expression(expr["args"][i], symbol_table))
    except Exception as e:  
        raise_my_error(str(e), expr) 

    fn_res, is_return, is_break = run_block(func_node["body"], local_symbol_table)
    try: 
        assign_var(symbol_table, "IT", fn_res)  # Store return value (or None/NOOB on GTFO) in IT
        notify_symbol_table(symbol_table)
    except Exception as e:  # Catch symbol table error if IT missing
        raise_my_error(str(e), expr)  
    return fn_res

# =========================================================
# STATEMENTS SECTION
# =========================================================
def run_block(statements, symbol_table):
    # Run statements one by one until a return, break, or the end
    res_val = None
    is_return = False
    is_break = False

    for stmt in statements:
        res_val, is_return, is_break = run_statement(stmt, symbol_table)
        # Exit early if the statement returned or broke out
        if is_return or is_break:
            return res_val, is_return, is_break

    return None, False, False

# ========================================
def run_statement(stmt, symbol_table):
    # Run one statement based on its type
    stype = stmt["type"]
    res_val = None
    is_return = False
    is_break = False

    if stype == "ASSIGN":
        val = eval_expression(stmt["expr"], symbol_table)
        try:
            assign_var(symbol_table, stmt["name"], val)
            notify_symbol_table(symbol_table)
        except Exception as e: 
            raise_my_error(str(e), stmt)

    elif stype == "RECAST":
        # Change variable type in place
        try:
            current_val = get_var_value(symbol_table, stmt["name"])
            assign_var(symbol_table, stmt["name"], do_cast(current_val, stmt["target_type"], stmt))
            notify_symbol_table(symbol_table)
        except InterpreterRuntimeError:  # Preserve existing error line info
            raise  # Stop loop execution immediately
        except Exception as e:  
            raise_my_error(str(e), stmt)  

    elif stype == "VISIBLE":
        out_str = ""
        for arg in stmt["args"]:
            out_str = out_str + to_string(eval_expression(arg, symbol_table), stmt)
        if not stmt.get("no_newline"):
            out_str = out_str + "\n"
        print_func(out_str)

    elif stype == "GIMMEH":
        # Save user input as text
        val_input = str(input_func("")) 
        try: 
            assign_var(symbol_table, stmt["name"], val_input)
            notify_symbol_table(symbol_table)
        except Exception as e: 
            raise_my_error(str(e), stmt)

    elif stype == "EXPR_STMT":
        # Save standalone expression results into IT
        val = eval_expression(stmt["expr"], symbol_table) 
        try:
            assign_var(symbol_table, "IT", val)
            notify_symbol_table(symbol_table)
        except Exception as e: 
            raise_my_error(str(e), stmt)

    elif stype == "IF_STMT":
        res_val, is_return, is_break = run_if_stmt(stmt, symbol_table)

    elif stype == "SWITCH_STMT":
        res_val, is_return, is_break = run_switch_stmt(stmt, symbol_table)

    elif stype == "LOOP_STMT":
        res_val, is_return, is_break = run_loop_stmt(stmt, symbol_table)

    elif stype == "FUNC_DEF":
        # Save function so it can be called later
        my_functions[stmt["name"]] = stmt

    elif stype == "RETURN":
        res_val = eval_expression(stmt["expr"], symbol_table)
        is_return = True

    elif stype == "GTFO":
        is_break = True

    else:
        raise_my_error("Unknown statement type: " + str(stype), stmt)

    return res_val, is_return, is_break

# ========================================
def run_if_stmt(stmt, symbol_table):
    # Check IT first, then else-if branches, then else
    try: 
        it_val = get_var_value(symbol_table, "IT") 
    except Exception as e:  
        raise_my_error(str(e), stmt)

    if to_bool(it_val):
        return run_block(stmt["then_block"], symbol_table)

    # Check each else-if condition in order
    for cond, block in stmt["mebbe_blocks"]:
        if to_bool(eval_expression(cond, symbol_table)):
            return run_block(block, symbol_table)

    return run_block(stmt["else_block"], symbol_table)

# ========================================
def run_switch_stmt(stmt, symbol_table):
    # Match IT against cases and run matching blocks until GTFO
    try: 
        it_val = get_var_value(symbol_table, "IT")  
    except Exception as e:  
        raise_my_error(str(e), stmt)

    matched = False
    res_val = None
    is_return = False
    is_break = False

    for case_expr, block in stmt["cases"]:
        if not matched:
            matched = check_equals(it_val, eval_expression(case_expr, symbol_table))
        if matched:
            res_val, is_return, is_break = run_block(block, symbol_table)
            if is_return or is_break:
                return res_val, is_return, is_break

    res_val, is_return, is_break = run_block(stmt["default_block"], symbol_table)
    return res_val, is_return, is_break

# ========================================
def run_loop_stmt(stmt, symbol_table):
    # Run loop with optional stop condition and step change
    var_name = stmt["var_name"]
    res_val = None
    is_return = False

    while True:
        if stmt.get("cond_expr") is not None:
            cond_val = to_bool(eval_expression(stmt["cond_expr"], symbol_table))
            # Stop TIL when true; stop WILE when false
            if stmt["cond_type"] == "TIL" and cond_val:
                break
            if stmt["cond_type"] == "WILE" and not cond_val:
                break

        res_val, is_return, is_break = run_block(stmt["body"], symbol_table)
        if is_return:
            return res_val, True, False
        if is_break:
            break

        try: 
            curr = to_num(get_var_value(symbol_table, var_name), stmt)  # Read and convert loop counter
            if stmt["operation"] == "UPPIN":
                assign_var(symbol_table, var_name, curr + 1)  # Increment loop counter
            else:
                assign_var(symbol_table, var_name, curr - 1)  # Decrement loop counter
            notify_symbol_table(symbol_table)
        except InterpreterRuntimeError:   # Preserve existing error line info
            raise  # Stop loop execution immediately
        except Exception as e: 
            raise_my_error(str(e), stmt)  

    return None, False, False


# =========================================================
# MAIN PROGRAM INTERPRETER
# =========================================================
def interpret_program(ast, output_override=None, input_override=None, symbol_table_override=None):
    # Set up I/O overrides, collect functions and variables, then run code
    global my_functions, print_func, input_func, update_table_func
    my_functions = {}

    if output_override is not None:
        print_func = output_override
    else:
        print_func = lambda text: print(text, end="")
        
    if input_override is not None:
        input_func = input_override
    else:
        input_func = input

    update_table_func = symbol_table_override

    symbol_table = create_symbol_table()
    notify_symbol_table(symbol_table)

    # Save functions first so they can be called anywhere
    for stmt in ast["body"]:
        if stmt["type"] == "FUNC_DEF":
            my_functions[stmt["name"]] = stmt

    # Set up initial variables before running main statements
    for decl in ast["declarations"]:
        val = None
        if decl["init"] is not None:
            val = eval_expression(decl["init"], symbol_table)
        try:  
            declare_var(symbol_table, decl["name"], val)
            notify_symbol_table(symbol_table)
        except Exception as e:  
            raise_my_error(str(e), decl)

    run_block(ast["body"], symbol_table)

    return symbol_table