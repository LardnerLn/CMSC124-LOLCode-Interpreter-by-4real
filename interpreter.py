from symbol_table import SymbolTable
from lexer import read_lexemes

class SyntaxErrorLOL(Exception):
    # Custom exception for syntax/runtime errors
    pass

class Interpreter:
    def __init__(self, token_list):
        self.tokens = token_list
        self.pos = 0
        self.table = SymbolTable()
        self.should_gtfo = False

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_lexeme(self):
        token = self.current_token()
        return token[1] if token else None

    def peek_category(self):
        token = self.current_token()
        return token[2] if token else None

    def advance(self):
        token = self.current_token()
        self.pos += 1
        return token

    def match(self, expected_lexeme):
        token = self.current_token()
        if token and token[1] == expected_lexeme:
            self.advance()
            return token
        return None

    def expect(self, expected_lexeme, error_context=""):
        token = self.match(expected_lexeme)
        if not token:
            curr = self.current_token()
            line = curr[0] if curr else "EOF"
            lexeme = curr[1] if curr else "end of file"
            raise SyntaxErrorLOL(f"Error on line {line}: Expected '{expected_lexeme}', found '{lexeme}'. {error_context}")
        return token

    def interpret(self):
        # Sinimulan ko muna yung flow ng program
        self.parse_program()

    def parse_program(self):
        # <program> ::= HAI <wazzup-sec> <statement-block> KTHXBYE
        self.expect("HAI", "Program must start with 'HAI'.")

        if self.peek_lexeme() == "WAZZUP":
            self.parse_wazzup_block()

        # Statement block execution loop hanggang KTHXBYE
        while self.current_token() and self.peek_lexeme() != "KTHXBYE":
            self.parse_statement()

        self.expect("KTHXBYE", "Program must end with 'KTHXBYE'.")

        if self.current_token():
            curr = self.current_token()
            raise SyntaxErrorLOL(f"Error on line {curr[0]}: Unexpected token '{curr[1]}' after KTHXBYE.")

    def parse_wazzup_block(self):
        # WAZZUP declarations setup
        self.expect("WAZZUP", "Expected 'WAZZUP'.")
        while self.current_token() and self.peek_lexeme() != "BUHBYE":
            self.parse_var_declaration()
        self.expect("BUHBYE", "Expected 'BUHBYE'.")

    def parse_var_declaration(self):
            # Variable declaration at ITZ handling
            self.expect("I HAS A", "Variable declaration must start with 'I HAS A'.")
            curr = self.current_token()
            if not curr or curr[2] != "Identifier":
                line = curr[0] if curr else "EOF"
                raise SyntaxErrorLOL(f"Error on line {line}: Expected variable name.")
            
            var_name = curr[1]
            self.advance()

            initial_val = None
            if self.match("ITZ"):
                
          
                while self.current_token() and self.peek_lexeme() != "BUHBYE" and self.current_token()[0] == curr[0]:
                    self.advance()

            self.table.declare(var_name, initial_val)

    def parse_statement(self):
        # TODO: 
        pass

    def parse_visible(self):
        # TODO:
        pass

    def parse_expression(self):
        # TODO: 
        pass

#more todo gaiz mehwehwh

if __name__ == "__main__":
    try:
        tokens = read_lexemes("ownsample.lol")
        interpreter = Interpreter(tokens)
        interpreter.interpret()
        interpreter.table.print_table()
    except Exception as e:
        print(f"Runtime Error: {e}")