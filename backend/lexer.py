import re

# Lexemes classifiers based on Project Requirement 1
LITERALS = [
    ("YARN",   "String Literal",  re.compile(r'^"[^"]*"$')),  # Allows colons (:) and special chars in string literals
    ("NUMBAR", "Float Literal",   re.compile(r'^-?[0-9]+\.[0-9]+$')),
    ("NUMBR",  "Integer Literal", re.compile(r'^-?[0-9]+$')),
    ("TROOF",  "Boolean Literal", re.compile(r'^(WIN|FAIL)$')),
    ("TYPE",   "Type Literal",    re.compile(r'^(NOOB|NUMBR|NUMBAR|YARN|TROOF)$')),
]

# Dictionary for keyword categorization
KEYWORD_CATEGORIES = {
    "Start Code": ["HAI"],
    "End Code": ["KTHXBYE"],
    "Data Type": ["NUMBR", "NUMBAR", "YARN", "TROOF", "NOOB"],
    # Separate token labels for WAZZUP and BUHBYE instead of sharing Variable Statement
    "Variable Declaration Start": ["WAZZUP"],
    "Variable Declaration End": ["BUHBYE"],
    "Variable Declaration": ["I HAS A"],
    "Variable Statement": ["ITZ", "R"],
    "I/O Statement": ["VISIBLE", "GIMMEH"],
    "Arithmetic Operator": ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"],
    "Logical Operator": ["BOTH OF", "EITHER OF", "WON OF", "NOT", "ALL OF", "ANY OF"],
    "Comparison Operator": ["BOTH SAEM", "DIFFRINT"],
    "String/Typecast Operator": ["SMOOSH", "MAEK", "A", "IS NOW A"],
    "Conditional/Control Statement": ["O RLY?", "YA RLY", "MEBBE", "NO WAI", "OIC", "WTF?", "OMG", "OMGWTF", "GTFO"],
    "Loop Statement": ["IM IN YR", "IM OUTTA YR", "UPPIN", "NERFIN", "YR", "TIL", "WILE"],
    "Function Statement": ["HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ"],
}

KEYWORDS = []
for words in KEYWORD_CATEGORIES.values():
    KEYWORDS.extend(words)
KEYWORDS.extend(["BTW", "OBTW", "TLDR", "MKAY", "AN", "+"])

KEYWORD_REGEX = [(word, re.compile("^" + re.escape(word) + "$")) for word in KEYWORDS]
IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
KEYWORDS_SORTED = sorted(KEYWORDS, key=len, reverse=True)

# =========================================================
def classify(lexeme):
    # Classifies a lexeme as a Literal, Keyword, or Identifier
    if isinstance(lexeme, tuple) and lexeme[0] == "__YARN__":
        return ("Literal (YARN)", "String Literal")

    if lexeme == '"':
        return ("String Delimiter", "String Delimiter")

    # Check for comment keywords
    if lexeme in ["BTW", "OBTW", "TLDR"]:
        return ("Comment Keyword", "Comment Keyword")

    for name, label, regex in LITERALS:
        if regex.match(lexeme):
            return (f"Literal ({name})", label)

    for word, regex in KEYWORD_REGEX:
        # Match exact case so only uppercase keywords are recognized
        if regex.match(lexeme):
            for category, words in KEYWORD_CATEGORIES.items():
                if word in words:
                    return ("KEYWORD", category)
            return ("KEYWORD", "Keyword")

    if IDENTIFIER.match(lexeme):
        return ("Identifier", "Variable Identifier")

    # Check if it's comment text content
    if isinstance(lexeme, str) and not lexeme.startswith('"') and not lexeme.startswith(("HAI", "KTHXBYE")):
        return ("Comment Text", "Comment Text")

    return ("INVALID", "Invalid")

# =========================================================
def read_file(filename):
    # Reads source lines from a file
    lines = []
    with open(filename, "r") as file:
        for line in file:
            lines.append(line.rstrip("\n"))
    return lines

# =========================================================
def tokenize(line):
    # Splits a single line into token strings
    tokens = []
    line = line.strip()
    i = 0
    line_length = len(line)

    while i < line_length:
        if line[i].isspace():
            i += 1
            continue

        if line[i] == '"':
            closing_quote = line.find('"', i + 1)
            tokens.append('"')
            if closing_quote != -1:
                inner_text = line[i + 1 : closing_quote]
                if inner_text != "":
                    tokens.append(("__YARN__", inner_text))
                tokens.append('"')
                i = closing_quote + 1
            else:
                inner_text = line[i + 1 :]
                if inner_text != "":
                    tokens.append(("__YARN__", inner_text))
                break
            continue

        is_comment = False
        for comment_kw in ["OBTW", "TLDR", "BTW"]:
            kw_len = len(comment_kw)
            if line[i : i + kw_len] == comment_kw:
                if (i + kw_len == line_length) or line[i + kw_len].isspace():
                    tokens.append(comment_kw)
                    comment_text = line[i + kw_len:].strip()
                    if comment_text:
                        tokens.append(comment_text)
                    is_comment = True
                    break

        if is_comment:
            break

        matched_keyword = None
        for keyword in KEYWORDS_SORTED:
            kw_len = len(keyword)
            if line[i : i + kw_len] == keyword:
                next_pos = i + kw_len
                if next_pos == line_length or not (line[next_pos].isalnum() or line[next_pos] == '_'):
                    matched_keyword = keyword
                    break

        if matched_keyword:
            tokens.append(matched_keyword)
            i += len(matched_keyword)
            continue

        start_index = i
        while i < line_length and not line[i].isspace():
            i += 1
        tokens.append(line[start_index:i])

    return tokens

# =========================================================
def tokenize_code(lines):
    # Tokenizes lines of code and includes comments
    tokenized_program = []
    multiline_comment = False

    TLDR_REGEX = re.compile(r'(?<!\S)TLDR(?!\S)')

    for line_number, raw_line in enumerate(lines, 1):
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue

        if multiline_comment:
            match = TLDR_REGEX.search(stripped_line)
            if match:
                multiline_comment = False
                line_tokens = ["TLDR"] + tokenize(stripped_line[match.end():])
                tokenized_program.append((line_number, line_tokens))
            else:
                tokenized_program.append((line_number, [stripped_line]))
            continue

        if stripped_line.split()[0] == "OBTW":
            line_tokens = ["OBTW"]
            match = TLDR_REGEX.search(stripped_line)
            if match:
                line_tokens += ["TLDR"] + tokenize(stripped_line[match.end():])
            else:
                multiline_comment = True
            tokenized_program.append((line_number, line_tokens))
            continue

        line_tokens = tokenize(raw_line)
        if line_tokens:
            tokenized_program.append((line_number, line_tokens))

    return tokenized_program

# =========================================================
def read_lexemes(filename):
    # Tokenizes and classifies lexemes from a file
    lines = read_file(filename)
    tokenized_program = tokenize_code(lines)
    classified_tokens = []

    for line_number, line_tokens in tokenized_program:
        for token in line_tokens:
            category, sub_type = classify(token)
            display_category = sub_type if sub_type else category
            lexeme_display = token[1] if isinstance(token, tuple) and token[0] == "__YARN__" else token
            classified_tokens.append((line_number, lexeme_display, display_category))

    return classified_tokens

# =========================================================
def print_token_table(tokens):
    # Displays formatted token table
    print("\n" + "=" * 55)
    print(f"{'Line':<6} | {'Lexeme':<24} | {'Category':<20}")
    print("=" * 55)
    for line_number, lexeme, category in tokens:
        print(f"{str(line_number):<6} | {str(lexeme):<24} | {str(category):<20}")
    print("=" * 55 + "\n")