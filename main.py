from lexer import read_lexemes, print_token_table
from parser import parse, SyntaxErrorLOL
from interpreter import Interpreter


def run_interpreter(filename):
    print(f"\n--- Loading and Lexing: {filename} ---")

    # Phase 1: Lexical Analysis
    tokens = read_lexemes(filename)
    print_token_table(tokens)

    # Phase 2: Syntax Analysis & Execution
    print("--- Starting Syntax Analysis & Execution ---")

    try:
        # Syntax check using parser
        if parse(tokens):
            print("SUCCESS: Program is syntactically valid!")

        # Semantic Execution & Symbol Table
        # interp = Interpreter(tokens)
        # interp.interpret()
        
        # Print the final symbol table state
        # interp.table.print_table()
    
    except SyntaxErrorLOL as e:
        print(f"\nFAILED: {e}")

run_interpreter("ownsample.lol")
#run_interpreter("sample.lol")