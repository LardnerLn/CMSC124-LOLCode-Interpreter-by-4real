import re

# Token definitions structured as (token_type, lexeme)
# Ordered by length (longest first)
TOKEN_DEFINITIONS = [
    # Multi-word keywords / Operators
    ("LOOP_OPERATOR", "IM OUTTA YR"),
    ("FUNCTION_OPERATOR", "HOW IZ I"),
    ("FUNCTION_OPERATOR", "IF U SAY SO"),
    ("FUNCTION_OPERATOR", "FOUND YR"),
    ("LOOP_OPERATOR", "IM IN YR"),
    ("ARITHMETIC_OPERATOR", "QUOSHUNT OF"),
    ("ARITHMETIC_OPERATOR", "PRODUKT OF"),
    ("ARITHMETIC_OPERATOR", "SMALLR OF"),
    ("TYPECAST_OPERATOR", "IS NOW A"),
    ("COMPARISON_OPERATOR", "BOTH SAEM"),
    ("BOOLEAN_OPERATOR", "EITHER OF"),
    ("ARITHMETIC_OPERATOR", "BIGGR OF"),
    ("ARITHMETIC_OPERATOR", "SUM OF"),
    ("ARITHMETIC_OPERATOR", "DIFF OF"),
    ("ARITHMETIC_OPERATOR", "MOD OF"),
    ("BOOLEAN_OPERATOR", "BOTH OF"),
    ("BOOLEAN_OPERATOR", "WON OF"),
    ("BOOLEAN_OPERATOR", "ALL OF"),
    ("BOOLEAN_OPERATOR", "ANY OF"),
    ("VAR_DECLARATION", "I HAS A"),
    ("CONDITION_OPERATOR", "O RLY?"),
    ("CONDITION_OPERATOR", "YA RLY"),
    ("CONDITION_OPERATOR", "NO WAI"),
    ("SWITCH_OPERATOR", "OMGWTF"),
    ("SWITCH_OPERATOR", "WTF?"),
    ("FUNCTION_OPERATOR", "I IZ"),

    # Single-word keywords / Operators
    ("CODE_DELIMITER", "KTHXBYE"),
    ("WAZZUP_SECTION", "WAZZUP"),
    ("WAZZUP_SECTION", "BUHBYE"),
    ("COMPARISON_OPERATOR", "DIFFRINT"),
    ("OUTPUT_OPERATOR", "VISIBLE"),
    ("INPUT_OPERATOR", "GIMMEH"),
    ("CONCATENATION_OPERATOR", "SMOOSH"),
    ("LOOP_OPERATOR", "UPPIN"),
    ("LOOP_OPERATOR", "NERFIN"),
    ("CONDITION_OPERATOR", "MEBBE"),
    ("TYPECAST_OPERATOR", "MAEK"),
    ("FUNCTION_OPERATOR", "GTFO"),
    ("DELIMITER", "MKAY"),
    ("CODE_DELIMITER", "HAI"),
    ("VAR_INITIALIZATION", "ITZ"),
    ("CONDITION_OPERATOR", "OIC"),
    ("SWITCH_OPERATOR", "OMG"),
    ("LOOP_OPERATOR", "TIL"),
    ("LOOP_OPERATOR", "WILE"),
    ("BOOLEAN_OPERATOR", "NOT"),
    ("LOOP_OPERATOR", "YR"),
    ("SEPARATOR", "AN"),
    ("TYPECAST_A", "A"),
    ("ASSIGNMENT_OPERATOR", "R"),
]

TYPE_LITERALS = {"NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF"}
TROOF_LITERALS = {"WIN", "FAIL"}

# Regex
IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
NUMBAR_REGEX = re.compile(r'^-?[0-9]+\.[0-9]+$')
NUMBR_REGEX = re.compile(r'^-?[0-9]+$')

def tokenize(source_code):

    # tokenizes LOLCODE source code into an ordered list of tuples: (token_type, lexeme).
    # returns (tokens, errors, line_statements).

    tokens = []
    errors = []
    line_statements = [] # holds statement boundary info for parsing in later milestones[cite: 4]

    lines = source_code.splitlines()
    in_multiline_comment = False
    obtw_start_line = -1 #no active OBTW block has started yet
    obtw_start_col = -1 #no active OBTW column tracked yet

    for line_idx, line in enumerate(lines):
        line_number = line_idx + 1
        col = 0
        line_len = len(line)

        # Handle multiline comments
        if in_multiline_comment:
            tldr_pos = line.find("TLDR")
            if tldr_pos != -1:
                in_multiline_comment = False
                col = tldr_pos + 4
            else:
                continue

        line_token_start_idx = len(tokens)

        while col < line_len:
            # skip non newline whitespace
            if line[col] in " \t\r":
                col += 1
                continue

            # single line comment check (BTW)
            if line[col:col + 3] == "BTW":
                # ensure word boundary
                if col + 3 == line_len or line[col + 3] in " \t\r":
                    break # Ignore rest of the line

            # multiline comment start check (OBTW)
            if line[col:col + 4] == "OBTW":
                if col + 4 == line_len or line[col + 4] in " \t\r":
                    in_multiline_comment = True
                    obtw_start_line = line_number
                    obtw_start_col = col + 1
                    break

            # 1. Check Token Definitions (Keywords / Operators)
            matched_token = False
            for token_type, lexeme in TOKEN_DEFINITIONS:
                lexeme_len = len(lexeme)
                
                if line[col:col + lexeme_len] == lexeme:
                    # enforce word boundary
                    next_char_idx = col + lexeme_len
                    
                    if next_char_idx == line_len or line[next_char_idx] in " \t\r,+" or lexeme in ["O RLY?", "WTF?"]:
                        tokens.append((token_type, lexeme))
                        col += lexeme_len
                        matched_token = True
                        break

            if matched_token:
                continue

            # 2. String Literal (YARN)
            if line[col] == '"':
                start_col = col + 1
                end_quote = line.find('"', col + 1)
                
                if end_quote != -1:
                    yarn_lexeme = line[col:end_quote + 1]
                    tokens.append(("YARN_LITERAL", yarn_lexeme))
                    col = end_quote + 1
                else:
                    errors.append(f"Line {line_number}, Col {start_col}: Unterminated YARN literal.")
                    col = line_len
                
                continue

            # 3. VISIBLE '+' Separator
            if line[col] == '+':
                tokens.append(("VISIBLE_SEPARATOR", "+"))
                col += 1
                continue

            # 4. Extract continuous non whitespace token chunk
            start_col = col + 1
            chunk_match = re.match(r'[^\s+,]+', line[col:])
            
            if chunk_match:
                chunk = chunk_match.group(0)
                
                # check type literals
                if chunk in TYPE_LITERALS:
                    tokens.append(("TYPE_LITERAL", chunk))
                    col += len(chunk)
                    continue

                # check TROOF literals
                if chunk in TROOF_LITERALS:
                    tokens.append(("TROOF_LITERAL", chunk))
                    col += len(chunk)
                    continue

                # check NUMBAR literal
                if NUMBAR_REGEX.match(chunk):
                    tokens.append(("NUMBAR_LITERAL", chunk))
                    col += len(chunk)
                    continue

                # check NUMBR literal
                if NUMBR_REGEX.match(chunk):
                    tokens.append(("NUMBR_LITERAL", chunk))
                    col += len(chunk)
                    continue

                # check identifiers
                if IDENTIFIER_REGEX.match(chunk):
                    tokens.append(("IDENTIFIER", chunk))
                    col += len(chunk)
                    continue

                # if no pattern matches, it's a lexical error
                errors.append(f"Line {line_number}, Col {start_col}: Unrecognized token '{chunk}'")
                col += len(chunk)
            
            else:
                errors.append(f"Line {line_number}, Col {col + 1}: Unexpected character '{line[col]}'")
                col += 1

        if len(tokens) > line_token_start_idx:
            line_statements.append((line_number, line_token_start_idx, len(tokens)))

    if in_multiline_comment:
        errors.append(f"Line {obtw_start_line}, Col {obtw_start_col}: Unclosed multiline comment (OBTW without TLDR).")

    return tokens, errors, line_statements