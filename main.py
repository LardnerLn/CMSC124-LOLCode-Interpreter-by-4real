from lexer import read_lexemes, print_token_table
from parser import parse, SyntaxErrorLOL


def run_interpreter(filename):
    print(f"\n--- Loading and Lexing: {filename} ---")

    # Phase 1: Lexical Analysis
    tokens = read_lexemes(filename)
    print_token_table(tokens)

    # Phase 2: Syntax Analysis
    print("--- Starting Syntax Analysis (Parser) ---")

    try:
        if parse(tokens):
            print("SUCCESS: Program is syntactically valid!")
    
    except SyntaxErrorLOL as e:
        print(f"\nFAILED: {e}")



run_interpreter("sample.lol")