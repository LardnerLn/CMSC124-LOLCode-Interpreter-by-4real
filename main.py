import re

# Lexemes classifiers (all are based on submitted project requirement 1)
LITERALS = [
    ("YARN",   re.compile(r'^"(:[)>o":]|[^":])*"$')),
    ("NUMBAR", re.compile(r'^-?[0-9]+\.[0-9]+$')),
    ("NUMBR",  re.compile(r'^-?[0-9]+$')),
    ("TROOF",  re.compile(r'^(WIN|FAIL)$')),
    ("TYPE",   re.compile(r'^(NOOB|NUMBR|NUMBAR|YARN|TROOF)$')),
]

KEYWORDS = [
    "HAI", "KTHXBYE", "WAZZUP", "BUHBYE", "BTW", 
    "OBTW", "TLDR", "I HAS A", "ITZ", "R", 
    "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", 
    "BIGGR OF", "SMALLR OF", "BOTH OF", "EITHER OF", "WON OF", 
    "NOT", "ANY OF", "ALL OF", "BOTH SAEM", "DIFFRINT", 
    "SMOOSH", "MAEK", "A", "IS NOW A", "VISIBLE", 
    "GIMMEH", "O RLY?", "YA RLY", "MEBBE", "NO WAI", 
    "OIC", "WTF?", "OMG", "OMGWTF", "IM IN YR", 
    "UPPIN", "NERFIN", "YR", "TIL", "WILE", 
    "IM OUTTA YR", "HOW IZ I", "IF U SAY SO", "GTFO", "FOUND YR", 
    "I IZ", "MKAY"
]

# build a regex per keyword exactly like the table: ^KEYWORD$ (escaped for ? )
# re.escape() takes a string and puts a backslash in front of any character that has a special meaning in regex
KEYWORD_REGEX = [(word, re.compile("^" + re.escape(word) + "$")) for word in KEYWORDS]

IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')

KEYWORDS_SORTED = sorted(KEYWORDS, key=len, reverse=True)

# =======================================================
# Function that determines if the string input belongs to literal, keyword, or identifier
def classify(lexeme):
    # check if it's a literal
    for name, regex in LITERALS:
        if regex.match(lexeme):
            return ("LITERAL", name)

    # check if it's a keyword
    for word, regex in KEYWORD_REGEX:
        if regex.match(lexeme):
            return ("KEYWORD", word)

    # check if it's an identifier
    if IDENTIFIER.match(lexeme):
        return ("IDENTIFIER", None)

    # else invalid
    return ("INVALID", None)


# # test cases, you may delete this
# for s in ['HAI', 'WAZZUP', '42', '-3.14', '"hello"', 'WIN', 'NOOB', 'I HAS A', 'x_1', '9abc']:
#     print(f"{s} -> {classify(s)}")

# =======================================================
# Ayen [File Reader]
# Read the file and return its lines
def read_file(filename):
    lines = []
    file = open(filename, "r")

    for line in file:
        lines.append(line.rstrip("\n"))

    file.close()

    return lines

# Test the file reader
lines = read_file("sample.lol")

line_number = 1

for line in lines:
    print("Line", line_number, ":", line)
    line_number = line_number + 1

# =======================================================
# Frannie [Tokenizer]
#splits each lines into tokens
#tokenize(line)
def tokenize(line):
    tokens = []
    line = line.strip()  # remove leading and trailing whitespace
    
    i = 0
    line_length = len(line)
    
    while i < line_length:
        # skip any spaces between tokens
        if line[i].isspace():
            i += 1
            continue
            
        # handle YARN string literals (enclosed in double quotes)
        if line[i] == '"':
            closing_quote = line.find('"', i + 1)
            if closing_quote != -1:
                # extract full quoted string including spaces
                tokens.append(line[i : closing_quote + 1])
                i = closing_quote + 1
            else:
                # handle unclosed string gracefully
                tokens.append(line[i:])
                break
            continue
            
        # handle single line and multi-line comment markers (BTW, OBTW, TLDR)
        # check if the word starts with BTW, OBTW, or TLDR
        is_comment = False
        for comment_kw in ["OBTW", "TLDR", "BTW"]:
            kw_len = len(comment_kw)
            if line[i : i + kw_len] == comment_kw:
                # ensure it's a standalone word (followed by space or end of line)
                if (i + kw_len == line_length) or line[i + kw_len].isspace():
                    tokens.append(comment_kw)
                    is_comment = True
                    break
        
        if is_comment:
            # comment text after comment keywords on this line is ignored
            break
        # match multi word and single word keywords (longest match first)
        matched_keyword = None
        
        for keyword in KEYWORDS_SORTED:
            kw_len = len(keyword)
            if line[i : i + kw_len] == keyword:
                # verify word boundary so sub-words aren't matched inside identifiers/other words
                next_pos = i + kw_len
                if next_pos == line_length or not (line[next_pos].isalnum() or line[next_pos] == '_'):
                    matched_keyword = keyword
                    break
                    
        if matched_keyword:
            tokens.append(matched_keyword)
            i += len(matched_keyword)
            continue
            
        # extract standard tokens (identifiers, NUMBR, NUMBAR, and more)
        start_index = i
        while i < line_length and not line[i].isspace():
            i += 1
        tokens.append(line[start_index:i])
        
    return tokens

# =======================================================
# tokenize sample.lol line by line
def tokenize_file(filename):
    lines = read_file(filename)
    tokenized_program = []
    multiline_comment = False

    for line_number, raw_line in enumerate(lines, 1):
        stripped_line = raw_line.strip()
        
        # skip completely empty lines
        if not stripped_line:
            continue
        
        # check and handle multi-line comments
        if stripped_line == "OBTW":
            multiline_comment = True
            line_tokens = ["OBTW"]
        elif stripped_line == "TLDR":
            multiline_comment = False
            line_tokens = ["TLDR"]
        elif multiline_comment:
            # skip lines inside the OBTW..TLDR comment block
            continue
        else:
            # extract tokens for the current line
            line_tokens = tokenize(raw_line)

        # store or display the extracted tokens per line
        tokenized_program.append((line_number, line_tokens))

    return tokenized_program

# =======================================================
# Nailah [Lexeme extraction]
# Reads, tokenizes, classifies every token (category or keyword), and structures the lexemes
def read_lexemes(filename):
    # tokenize the file line by line
    tokenized_program = tokenize_file(filename)
    classified_tokens = []

    # iterate throigh each line and its tokens
    for line_number, line_tokens in tokenized_program:
        for token in line_tokens:
            # classify each token using the classify function
            category, keyword = classify(token)

            # determine what label to display
            if keyword:
                display_category = keyword
            else:
                display_category = category

            # store the formatted token tuple
            classified_tokens.append((line_number, token, display_category))

    return classified_tokens

# =======================================================
# Ayen [Output format]
def print_token_table(tokens):
    print("\n" + "=" * 50)
    print(f"{'Line':<6} | {'Lexeme':<22} | {'Category':<18}")
    print("=" * 50)
    
    for line_number, lexeme, category in tokens:
        print(f"{str(line_number):<6} | {str(lexeme):<22} | {str(category):<18}")
        
    print("=" * 50 + "\n")

# =======================================================
def main():
    all_lexemes = read_lexemes("sample.lol")

    # print the final table
    print_token_table(all_lexemes)

main()