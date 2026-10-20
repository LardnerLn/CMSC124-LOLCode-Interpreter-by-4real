import re

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

IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')