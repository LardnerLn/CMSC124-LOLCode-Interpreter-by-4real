# interpreter.py

import re
from symbol_table import create_symbol_table, declare_var, assign_var, get_var_value

# exception for runtime errors
class InterpreterRuntimeError(Exception):
    pass

# Global storage for functions and io 
my_functions = {}
print_func = print
input_func = input

def raise_my_error(msg, node=None):
    # raise error with line info
    if node is not None and "line" in node and node["line"] is not None:
        raise InterpreterRuntimeError("Error on line " + str(node["line"]) + ": " + msg)
    raise InterpreterRuntimeError("Runtime Error: " + msg)


# =========================================================
# TYPECASTING SECTION
# =========================================================
def get_data_type(val):
    # get value data type
    if val is None:
        return "NOOB"
    if isinstance(val, bool):
        return "TROOF"
    if isinstance(val, int):
        return "NUMBR"
    if isinstance(val, float):
        return "NUMBAR"
    return "YARN"

def to_bool(val):
    # convert value to bool
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if val == 0:
            return False
        else:
            return True
    if val == "":
        return False
    return True

def to_num(val, node):
    # convert value to number
    if val is None:
        raise_my_error("Noob cant be number", node)
    if isinstance(val, bool):
        if val == True:
            return 1
        else:
            return 0
    if isinstance(val, (int, float)):
        return val

    # parse string to number
    s = str(val).strip()
    if re.match(r'^-?[0-9]+$', s):
        return int(s)
    if re.match(r'^-?[0-9]+\.[0-9]+$', s):
        return float(s)
        
    raise_my_error("Cannot parse number: " + str(val), node)

def to_string(val, node, explicit=False):
    # convert value to yarn safely
    if val is None:
        # Kapag NOOB o None, mag-return ng empty string para sa VISIBLE (hindi mag-error)
        if not explicit:
            return ""
        return ""
    if isinstance(val, bool):
        if val == True:
            return "WIN"
        else:
            return "FAIL"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        # format float decimals
        temp_s = str(val)
        if "." in temp_s:
            p = temp_s.split(".")
            return p[0] + "." + p[1][:2]
        return temp_s
    return str(val)

def do_cast(val, target, node):
    # cast value to target
    if target == "TROOF":
        return to_bool(val)
    elif target == "NOOB":
        return None
    elif target == "YARN":
        return to_string(val, node, True)
    elif target == "NUMBR":
        if val is None:
            return 0
        return int(to_num(val, node))
    elif target == "NUMBAR":
        if val is None:
            return 0.0
        return float(to_num(val, node))
    else:
        raise_my_error("Unknown type: " + str(target), node)

def check_equals(a, b):
    # compare values safely
    t1 = get_data_type(a)
    t2 = get_data_type(b)
    if t1 in ["NUMBR", "NUMBAR"] and t2 in ["NUMBR", "NUMBAR"]:
        return a == b
    if t1 != t2:
        return False
    return a == b


# =========================================================
# EXPRESSIONS SECTION
# =========================================================
def eval_expression(expr, symbol_table):
    # evaluate expression node
    etype = expr["type"]

    if etype == "LITERAL":
        return expr["value"]
    elif etype == "VARIABLE":
        return get_var_value(symbol_table, expr["name"])
    elif etype == "BIN_OP":
        return eval_binary_op(expr, symbol_table)
    elif etype == "UNARY_OP":
        val = eval_expression(expr["operand"], symbol_table)
        return not to_bool(val)
    elif etype == "VARIADIC_BOOL":
        # process variadic arguments
        results = []
        for arg in expr["args"]:
            results.append(to_bool(eval_expression(arg, symbol_table)))
            
        if expr["op"] == "ALL OF":
            all_true = True
            for r in results:
                if not r:
                    all_true = False
                    break
            return all_true
        else:
            any_true = False
            for r in results:
                if r:
                    any_true = True
                    break
            return any_true
    elif etype == "SMOOSH":
        # concat all strings
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

def eval_binary_op(expr, symbol_table):
    # evaluate binary operator
    op = expr["op"]
    left = eval_expression(expr["left"], symbol_table)
    right = eval_expression(expr["right"], symbol_table)

    # check logical operations
    if op == "BOTH OF":
        return to_bool(left) and to_bool(right)
    elif op == "EITHER OF":
        return to_bool(left) or to_bool(right)
    elif op == "WON OF":
        return to_bool(left) != to_bool(right)
    elif op == "BOTH SAEM":
        return check_equals(left, right)
    elif op == "DIFFRINT":
        return not check_equals(left, right)

    # get numeric operands
    num_a = to_num(left, expr)
    num_b = to_num(right, expr)
    
    both_ints = False
    if isinstance(num_a, int) and isinstance(num_b, int):
        both_ints = True

    # process arithmetic operations
    if op == "SUM OF":
        return num_a + num_b
    elif op == "DIFF OF":
        return num_a - num_b
    elif op == "PRODUKT OF":
        return num_a * num_b
    elif op == "QUOSHUNT OF":
        if num_b == 0:
            raise_my_error("Division by zero error", expr)
        if both_ints:
            return int(num_a / num_b)
        return num_a / num_b
    elif op == "MOD OF":
        if num_b == 0:
            raise_my_error("Modulo zero error", expr)
        if both_ints:
            return num_a - num_b * int(num_a / num_b)
        return num_a % num_b
    elif op == "BIGGR OF":
        return max(num_a, num_b)
    elif op == "SMALLR OF":
        return min(num_a, num_b)

    raise_my_error("Unknown operator: " + str(op), expr)

def call_user_func(expr, symbol_table):
    # execute user function
    fname = expr["name"]
    if fname not in my_functions:
        raise_my_error("Function not found: " + str(fname), expr)

    func_node = my_functions[fname]
    params = func_node["params"]
    
    if len(expr["args"]) != len(params):
        raise_my_error("Argument count mismatch", expr)

    # create local symbol table
    local_symbol_table = create_symbol_table()
    for i in range(len(params)):
        declare_var(local_symbol_table, params[i], eval_expression(expr["args"][i], symbol_table))

    fn_res, is_return, is_break = run_block(func_node["body"], local_symbol_table)
    assign_var(symbol_table, "IT", fn_res)
    return fn_res


# =========================================================
# STATEMENTS SECTION
# =========================================================
def run_block(statements, symbol_table):
    # execute statement block
    res_val = None
    is_return = False
    is_break = False

    for stmt in statements:
        res_val, is_return, is_break = run_statement(stmt, symbol_table)
        if is_return or is_break:
            return res_val, is_return, is_break

    return None, False, False

def run_statement(stmt, symbol_table):
    # execute single statement
    stype = stmt["type"]
    res_val = None
    is_return = False
    is_break = False

    if stype == "ASSIGN":
        val = eval_expression(stmt["expr"], symbol_table)
        assign_var(symbol_table, stmt["name"], val)

    elif stype == "RECAST":
        current_val = get_var_value(symbol_table, stmt["name"])
        assign_var(symbol_table, stmt["name"], do_cast(current_val, stmt["target_type"], stmt))

    elif stype == "VISIBLE":
        # print output arguments
        out_str = ""
        for arg in stmt["args"]:
            out_str = out_str + to_string(eval_expression(arg, symbol_table), stmt)
        if not stmt.get("no_newline"):
            out_str = out_str + "\n"
        print_func(out_str)

    elif stype == "GIMMEH":
        # get user input
        val_input = str(input_func(stmt["name"] + ": "))
        assign_var(symbol_table, stmt["name"], val_input)

    elif stype == "EXPR_STMT":
        assign_var(symbol_table, "IT", eval_expression(stmt["expr"], symbol_table))

    elif stype == "IF_STMT":
        res_val, is_return, is_break = run_if_stmt(stmt, symbol_table)

    elif stype == "SWITCH_STMT":
        res_val, is_return, is_break = run_switch_stmt(stmt, symbol_table)

    elif stype == "LOOP_STMT":
        res_val, is_return, is_break = run_loop_stmt(stmt, symbol_table)

    elif stype == "FUNC_DEF":
        my_functions[stmt["name"]] = stmt

    elif stype == "RETURN":
        res_val = eval_expression(stmt["expr"], symbol_table)
        is_return = True

    elif stype == "GTFO":
        is_break = True

    else:
        raise_my_error("Unknown statement type: " + str(stype), stmt)

    return res_val, is_return, is_break

def run_if_stmt(stmt, symbol_table):
    # execute if condition
    it_val = get_var_value(symbol_table, "IT")
    if to_bool(it_val):
        return run_block(stmt["then_block"], symbol_table)

    for cond, block in stmt["mebbe_blocks"]:
        if to_bool(eval_expression(cond, symbol_table)):
            return run_block(block, symbol_table)

    return run_block(stmt["else_block"], symbol_table)

def run_switch_stmt(stmt, symbol_table):
    # execute switch cases
    it_val = get_var_value(symbol_table, "IT")
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

def run_loop_stmt(stmt, symbol_table):
    # execute loop block
    var_name = stmt["var_name"]
    res_val = None
    is_return = False

    while True:
        # check loop condition
        if stmt.get("cond_expr") is not None:
            cond_val = to_bool(eval_expression(stmt["cond_expr"], symbol_table))
            if stmt["cond_type"] == "TIL" and cond_val:
                break
            if stmt["cond_type"] == "WILE" and not cond_val:
                break

        res_val, is_return, is_break = run_block(stmt["body"], symbol_table)
        if is_return:
            return res_val, True, False
        if is_break:
            break

        # update loop counter
        curr = to_num(get_var_value(symbol_table, var_name), stmt)
        if stmt["operation"] == "UPPIN":
            assign_var(symbol_table, var_name, curr + 1)
        else:
            assign_var(symbol_table, var_name, curr - 1)

    return None, False, False


# =========================================================
# MAIN PROGRAM INTERPRETER
# =========================================================
def interpret_program(ast, output_override=None, input_override=None):
    # main runner function
    global my_functions, print_func, input_func
    my_functions = {}

    # setup output function
    if output_override is not None:
        print_func = output_override
    else:
        print_func = lambda text: print(text, end="")
        
    # setup input function
    if input_override is not None:
        input_func = input_override
    else:
        input_func = input

    symbol_table = create_symbol_table()

    # scan function definitions first
    for stmt in ast["body"]:
        if stmt["type"] == "FUNC_DEF":
            my_functions[stmt["name"]] = stmt

    # initialize global variables
    for decl in ast["declarations"]:
        val = None
        if decl["init"] is not None:
            val = eval_expression(decl["init"], symbol_table)
        declare_var(symbol_table, decl["name"], val)

    # run main statement block
    run_block(ast["body"], symbol_table)

    return symbol_table