# symbol_table.py
# Simple procedural symbol table management using a Python dictionary

def create_symbol_table():
    # Creates and returns a fresh symbol table dictionary initialized with IT
    table = {}
    table["IT"] = None
    return table

def declare_var(table, name, value=None):
    # Adds a new variable to the symbol table
    if name in table:
        raise Exception("Variable '" + str(name) + "' is already declared.")
    table[name] = value

def assign_var(table, name, value):
    # Updates an existing variable in the symbol table
    if name not in table:
        raise Exception("Variable '" + str(name) + "' has not been declared.")
    table[name] = value

def get_var_value(table, name):
    # Looks up and returns the value of a variable
    if name not in table:
        raise Exception("Variable '" + str(name) + "' has not been declared.")
    return table[name]

def format_symbol_value(value):
    if value is None:  # Represent uninitialized / no-return None as NOOB
        return "NOOB"  
    if isinstance(value, bool):  # Check bool before int
        return "WIN" if value else "FAIL"  # Use WIN/FAIL instead of True/False
    return str(value)  # Keep standard string representation for other values

def print_symbol_table(table):
    # Prints the contents of the symbol table formatted as a table
    print("\n================ SYMBOL TABLE ================")
    print(f"{'Identifier':<15} | {'Value':<20}")
    print("----------------------------------------------")
    for name, value in table.items():
        print(f"{str(name):<15} | {format_symbol_value(value):<20}")
    print("==============================================\n")