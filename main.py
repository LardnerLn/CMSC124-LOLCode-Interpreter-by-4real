# main.py
import lexer
# import parser 

def main():
    filename = "sample.lol"
    
    print(f"Running lexical analysis on {filename}...")
    
    # run lexer to extract and classify lexemes
    all_lexemes = lexer.read_lexemes(filename)
    
    # print the token table
    lexer.print_token_table(all_lexemes)
    
    # insert parser call

    main()