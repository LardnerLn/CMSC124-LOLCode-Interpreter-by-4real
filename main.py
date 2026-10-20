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


#Ayen [File Reader]
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


#Member 3 [Tokenizer]
#splits each lines into tokens
#tokenize(line)


#Member 4 [Lexeme Extraction & integration]
#Combines tokens into complete lexemes and integrates the functions.
#read_lexemes(line)

# [Ayen] for output format
def print_token_table(tokens):
    print("\n" + "=" * 50)
    print(f"{'Line':<6} | {'Lexeme':<22} | {'Category':<18}")
    print("=" * 50)
    
    for line_num, lexeme, category in tokens:
        print(f"{str(line_num):<6} | {str(lexeme):<22} | {str(category):<18}")
        
    print("=" * 50 + "\n")
