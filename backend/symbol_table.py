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

def print_symbol_table(table):
    # Prints the contents of the symbol table formatted as a table
    print("\n================ SYMBOL TABLE ================")
    print(f"{'Identifier':<15} | {'Value':<20}")
    print("----------------------------------------------")
    for name, value in table.items():
        print(f"{str(name):<15} | {str(value):<20}")
    print("==============================================\n")