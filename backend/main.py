# main.py

from lexer import read_lexemes, print_token_table
from parser import parse, SyntaxErrorLOL
from sem_analyzer import analyze_semantics, SemanticErrorLOL
from interpreter import interpret_program, InterpreterRuntimeError
from symbol_table import print_symbol_table

def run_interpreter(filename):
    print("\n--- Loading and Lexing: " + str(filename) + " ---")

    # Phase 1: Lexical Analysis
    tokens = read_lexemes(filename)
    print_token_table(tokens)

    # Phase 2: Syntax Analysis & AST Generation
    print("--- Starting Syntax Analysis & AST Construction ---")

    try:
        ast = parse(tokens)
        print("SUCCESS: Program is syntactically valid!")

        # Phase 3: Semantic Analysis
        print("\n--- Starting Semantic Analysis ---")
        analyze_semantics(ast)
        print("SUCCESS: Program passed Semantic Analysis!")

        # Phase 4: Interpretation & Execution
        print("\n--- Program Execution Output ---")
        table = interpret_program(ast)

        # Print Symbol Table
        print_symbol_table(table)

    except SyntaxErrorLOL as e:
        print("\nSYNTAX ERROR FAILED: " + str(e))
    except SemanticErrorLOL as e:
        print("\nSEMANTIC ERROR FAILED: " + str(e))
    except InterpreterRuntimeError as e:
        print("\nRUNTIME ERROR FAILED: " + str(e))


# Point directly to any test case in your project folder
run_interpreter("../project-testcases/04_smoosh_assign.lol")