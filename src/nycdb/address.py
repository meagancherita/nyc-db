"""
Functions to standardize address strings
in HPD contacts data
"""
import re
# from collections import namedtuple

STREETS = [
    ( '(?<= )AVE(NUE)?', 'AVENUE' ),
    ( '(?<= )(STREET|STR|(ST\.?))', 'STREET' ),
    ( '(?<= )PL(ACE)?', 'PLACE'),
    ( '(?<= )(ROAD|(?<!\d)RD\.?)', 'ROAD' ),
    ( '(?<= )(LA(NE)?|LN)', 'LANE'),
    ( '(?<= )CT|CRT', 'COURT'),
    ( '(?<= )DR', 'DRIVE'),
    ( '(?<= )(BOULEVARD|BLVD)', 'BOULEVARD' ),
    ( '(?<= )(PKWY|PARKWY)', 'PARKWAY' ),
    ( '(^|(?<= ))(BDWAY|BDWY|BROAD WAY)', 'BROADWAY' )
]

DIRECTIONS = [
    ( "(^|(?<=[ ]))N\.?((?=[ ])|$)", 'NORTH'),
    ( "(^|(?<=[ ]))SO?\.?((?=[ ])|$)", 'SOUTH'),
    ( "(^|(?<=[ ]))E\.?((?=[ ])|$)", 'EAST'),
    ( "(^|(?<=[ ]))W\.?((?=[ ])|$)", 'WEST')
]

REMOVE = [
    ( '(BKLYN|BROOKLYN|QUEENS|BRONX|MANHATTAN|NEW YORK|NYC|SI)$', ''),
    ( 'BENSONHURST$', ''),
    ( '\(.+\)$', '')
]

REGEX_REPLACEMENTS = STREETS + DIRECTIONS + REMOVE

# Str, Str -> Lambda
def replace_func(pattern, replacement):
    return lambda s: re.sub(pattern, replacement, s)

REGEX_FUNCS = list(map(lambda x: replace_func(*x), REGEX_REPLACEMENTS))

WORD_NUMBERS = [ 'ZEROTH', 'FIRST', 'SECOND', 'THIRD',
                 'FOURTH', 'FIFTH', 'SIXTH', 'SEVENTH',
                 'EIGHTH', 'NINTH', 'TENTH' ]
SUFFIXES = {
    '0': 'TH',
    '1': 'ST', 
    '2': 'ND', 
    '3': 'RD',
    '4': 'TH',
    '5': 'TH',
    '6': 'TH',
    '7': 'TH',
    '8': 'TH',
    '9': 'TH'
}


def format_number(matchobj):
    n = matchobj.group('number')
    rest = matchobj.group('rest')
    if int(n) < 11:
        return WORD_NUMBERS[int(n)] + rest
    else:
        tens_digit = str(n)[-2:-1]

        if tens_digit == '1':
            return str(n) + 'TH' + rest
        else:
            return n + SUFFIXES[n[-1]] + rest


def replace_number(str):
    return re.sub("(^|(?<=[ ]))(?P<number>\d+)(TH|ST|ND|RD)?(?P<rest>(\b|[ ]).*)", format_number, str)


HOLY_SAINTS = [ 'JOSEPH', 'MARKS', 'LAWRENCE','JAMES',
                'NICHOLAS','HOLLIS', 'JOHNS',"JOHN's"]

SAINTS_REGEX = "ST\.?[ ](?P<street_name>({}))".format('|'.join(HOLY_SAINTS))

def saints(s):
    repl = lambda matchobj: "SAINT " + matchobj.group('street_name')
    return re.sub(SAINTS_REGEX, repl, s)


STREET_FUNCS = [replace_number, saints] + REGEX_FUNCS 

# list(of functions), str -> str
def func_chain(funcs, val):
    if len(funcs) == 0:
        return val
    else:
        return func_chain(funcs[1:],funcs[0](val))


def remove_extra_spaces(s):
    return ' '.join([x for x in s.split(' ') if x != ''])

def prepare(s):
    return remove_extra_spaces(s).strip().upper().replace('"', '').replace('-', '')

def normalize_street(street):
    return func_chain(STREET_FUNCS, prepare(street)).replace('.', '').strip()
