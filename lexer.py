import re

# Lexemes classifiers based on Project Requirement 1
LITERALS = [
    ("YARN",   re.compile(r'^"(:[)>o":]|[^":])*"$')),
    ("NUMBAR", re.compile(r'^-?[0-9]+\.[0-9]+$')),
    ("NUMBR",  re.compile(r'^-?[0-9]+$')),
    ("TROOF",  re.compile(r'^(WIN|FAIL)$')),
    ("TYPE",   re.compile(r'^(NOOB|NUMBR|NUMBAR|YARN|TROOF)$')),
]

# Dictionary for keyword categorization
KEYWORD_CATEGORIES = {
    "Start Code": ["HAI"],
    "End Code": ["KTHXBYE"],
    "Data Type": ["NUMBR", "NUMBAR", "YARN", "TROOF", "NOOB"],
    "Variable Statement": ["WAZZUP", "BUHBYE", "I HAS A", "ITZ", "R"],
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
KEYWORDS.extend(["BTW", "OBTW", "TLDR", "MKAY", "AN"])

KEYWORD_REGEX = [(word, re.compile("^" + re.escape(word) + "$")) for word in KEYWORDS]
IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
KEYWORDS_SORTED = sorted(KEYWORDS, key=len, reverse=True)


def classify(lexeme):
    #Classifies a lexeme as a Literal, Keyword, or Identifier
    for name, regex in LITERALS:
        if regex.match(lexeme):
            return ("Literal", name)

    for word, regex in KEYWORD_REGEX:
        if regex.match(lexeme.upper()):
            for category, words in KEYWORD_CATEGORIES.items():
                if word in words:
                    return ("KEYWORD", category)
            return ("KEYWORD", "Keyword")

    if IDENTIFIER.match(lexeme):
        return ("Identifier", None)

    return ("INVALID", None)


def read_file(filename):
    #Reads source lines from a file
    lines = []
    with open(filename, "r") as file:
        for line in file:
            lines.append(line.rstrip("\n"))
    return lines


def tokenize(line):
    #Splits a single line into token strings
    tokens = []
    line = line.strip()
    i = 0
    line_length = len(line)

    while i < line_length:
        if line[i].isspace():
            i += 1
            continue

        # String literal with spaces
        if line[i] == '"':
            closing_quote = line.find('"', i + 1)
            if closing_quote != -1:
                tokens.append(line[i : closing_quote + 1])
                i = closing_quote + 1
            else:
                tokens.append(line[i:])
                break
            continue

        # Comment keywords
        is_comment = False
        for comment_kw in ["OBTW", "TLDR", "BTW"]:
            kw_len = len(comment_kw)
            if line[i : i + kw_len] == comment_kw:
                if (i + kw_len == line_length) or line[i + kw_len].isspace():
                    tokens.append(comment_kw)
                    is_comment = True
                    break

        if is_comment:
            break

        # Multi-word and single-word keywords
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

        # Standard identifier or single word lexeme
        start_index = i
        while i < line_length and not line[i].isspace():
            i += 1
        tokens.append(line[start_index:i])

    return tokens


def tokenize_code(lines):
    #Tokenizes lines of code and filters out comments
    tokenized_program = []
    multiline_comment = False

    for line_number, raw_line in enumerate(lines, 1):
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue

        if stripped_line == "OBTW":
            multiline_comment = True
            continue
        elif stripped_line == "TLDR":
            multiline_comment = False
            continue
        elif multiline_comment:
            continue

        line_tokens = tokenize(raw_line)
        if line_tokens:
            tokenized_program.append((line_number, line_tokens))

    return tokenized_program


def read_lexemes(filename):
    #Tokenizes and classifies lexemes from a file
    lines = read_file(filename)
    tokenized_program = tokenize_code(lines)
    classified_tokens = []

    for line_number, line_tokens in tokenized_program:
        for token in line_tokens:
            category, sub_type = classify(token)
            if category == "KEYWORD":
                display_category = sub_type
            elif category == "Literal":
                display_category = f"Literal ({sub_type})"
            else:
                display_category = category

            classified_tokens.append((line_number, token, display_category))

    return classified_tokens


def print_token_table(tokens):
    #Displays formatted token table
    print("\n" + "=" * 55)
    print(f"{'Line':<6} | {'Lexeme':<24} | {'Category':<20}")
    print("=" * 55)
    for line_number, lexeme, category in tokens:
        print(f"{str(line_number):<6} | {str(lexeme):<24} | {str(category):<20}")
    print("=" * 55 + "\n")