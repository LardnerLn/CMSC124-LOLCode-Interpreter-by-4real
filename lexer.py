import re

# multiword and single word keywords ordered strictly by length/specificity (longest first)
KEYWORDS = [
    # Multi-word Keywords
    ("IM OUTTA YR", "LOOP_OPERATOR"),
    ("HOW IZ I", "FUNCTION_OPERATOR"),
    ("IF U SAY SO", "FUNCTION_OPERATOR"),
    ("FOUND YR", "FUNCTION_OPERATOR"),
    ("IM IN YR", "LOOP_OPERATOR"),
    ("QUOSHUNT OF", "ARITHMETIC_OPERATOR"),
    ("PRODUKT OF", "ARITHMETIC_OPERATOR"),
    ("SMALLR OF", "ARITHMETIC_OPERATOR"),
    ("IS NOW A", "TYPECAST_OPERATOR"),
    ("BOTH SAEM", "COMPARISON_OPERATOR"),
    ("EITHER OF", "BOOLEAN_OPERATOR"),
    ("BIGGR OF", "ARITHMETIC_OPERATOR"),
    ("SUM OF", "ARITHMETIC_OPERATOR"),
    ("DIFF OF", "ARITHMETIC_OPERATOR"),
    ("MOD OF", "ARITHMETIC_OPERATOR"),
    ("BOTH OF", "BOOLEAN_OPERATOR"),
    ("WON OF", "BOOLEAN_OPERATOR"),
    ("ALL OF", "BOOLEAN_OPERATOR"),
    ("ANY OF", "BOOLEAN_OPERATOR"),
    ("I HAS A", "VAR_DECLARATION"),
    ("O RLY?", "CONDITION_OPERATOR"),
    ("YA RLY", "CONDITION_OPERATOR"),
    ("NO WAI", "CONDITION_OPERATOR"),
    ("OMGWTF", "SWITCH_OPERATOR"),
    ("WTF?", "SWITCH_OPERATOR"),
    ("I IZ", "FUNCTION_OPERATOR"),

    # single word Keywords
    ("KTHXBYE", "CODE_DELIMITER"),
    ("WAZZUP", "WAZZUP_SECTION"),
    ("BUHBYE", "WAZZUP_SECTION"),
    ("DIFFRINT", "COMPARISON_OPERATOR"),
    ("VISIBLE", "OUTPUT_OPERATOR"),
    ("GIMMEH", "INPUT_OPERATOR"),
    ("SMOOSH", "CONCATENATION_OPERATOR"),
    ("UPPIN", "LOOP_OPERATOR"),
    ("NERFIN", "LOOP_OPERATOR"),
    ("MEBBE", "CONDITION_OPERATOR"),
    ("MAEK", "TYPECAST_OPERATOR"),
    ("GTFO", "FUNCTION_OPERATOR"),
    ("MKAY", "DELIMITER"),
    ("HAI", "CODE_DELIMITER"),
    ("ITZ", "VAR_INITIALIZATION"),
    ("OIC", "CONDITION_OPERATOR"),
    ("OMG", "SWITCH_OPERATOR"),
    ("TIL", "LOOP_OPERATOR"),
    ("WILE", "LOOP_OPERATOR"),
    ("NOT", "BOOLEAN_OPERATOR"),
    ("YR", "LOOP_OPERATOR"),
    ("AN", "SEPARATOR"),
    ("A", "TYPECAST_A"),
    ("R", "ASSIGNMENT_OPERATOR"),
]

TYPE_LITERALS = {"NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF"}
TROOF_LITERALS = {"WIN", "FAIL"}

IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
NUMBAR_REGEX = re.compile(r'^-?[0-9]+\.[0-9]+$')
NUMBR_REGEX = re.compile(r'^-?[0-9]+$')


def tokenize(source_code):

    # tokenizes LOLCODE source code into an ordered list of tuples: (token_type, lexeme).
    # returns (tokens, errors, line_statements).

    tokens = []
    errors = []
    line_statements = [] # holds statement boundary info for parsing in later milestones

    lines = source_code.splitlines()
    in_multiline_comment = False
    obtw_start_line = -1
    obtw_start_col = -1

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

            # 1. Check Keywords
            matched_keyword = False
            for kw, token_type in KEYWORDS:
                kw_len = len(kw)
                
                if line[col:col + kw_len] == kw:
                
                    # enforce word boundary
                    next_char_idx = col + kw_len
                
                    if next_char_idx == line_len or line[next_char_idx] in " \t\r,+" or kw in ["O RLY?", "WTF?"]:
                        tokens.append((token_type, kw))
                        col += kw_len
                
                        matched_keyword = True
                
                        break

            if matched_keyword:
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