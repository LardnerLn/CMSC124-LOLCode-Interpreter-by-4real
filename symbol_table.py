class SymbolTable:
    def __init__(self):
        # set up storage
        self.table = {}
        self.table["IT"] = None

    def declare(self, name, value=None):
        # add new var
        if name in self.table:
            raise Exception(f"Variable '{name}' already declared.")
        self.table[name] = value

    def assign(self, name, value):
        # update variable
        if name not in self.table:
            raise Exception(f"Variable '{name}' not declared.")
        self.table[name] = value

    def get_value(self, name):
        # lookup value
        if name not in self.table:
            raise Exception(f"Variable '{name}' not declared.")
        return self.table[name]

    def print_table(self):
        # print table
        print("\n================ SYMBOL TABLE ================")
        print(f"{'Identifier':<15} | {'Value':<20}")
        print("----------------------------------------------")
        for name, value in self.table.items():
            print(f"{name:<15} | {str(value):<20}")
        print("==============================================\n")

    def dump(self):
        # return copy
        return self.table.copy()


