import lexer

def main():
    sample_file_path = "sample.lol"

    # Open and read the file directly
    with open(sample_file_path, "r", encoding = "utf-8") as f:
        source_code = f.read()

    # Run lexical analysis
    tokens, errors, _ = lexer.tokenize(source_code)

    # Display detected tokens in a formatted table
    print("-" * 60)
    print(f"{'LEXEME':<30} | {'TOKEN CLASSIFICATION'}")
    print("-" * 60)
    
    for token_type, lexeme in tokens:
    
        print(f"{lexeme:<30} | {token_type}")
    
    print("-" * 60)

    # Display diagnostics / errors
    print("\n[LEXICAL DIAGNOSTICS]")
    
    if errors:
    
        for error in errors:
            print(f"  - {error}")
    else:
        print("  Lexical Analysis Successful: No errors found.")


main()