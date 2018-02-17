# ![εpsilon](logo.png)

## Introduction
Epsilon is a scanner generator.

It converts a sequence of regular expressions into a
[deterministic finite automaton
](https://en.wikipedia.org/wiki/Deterministic_finite_automaton).
The DFA accepts input that matches any of these expressions.
Each expression is associated with a token.
The generated scanner applies the DFA repeatedly to input text to 
return a sequence of tokens.

This manual is currently a work in progress and incomplete.
Contributions are welcome.

## Quick Start

Here is a simple input file, *example.epsilon*:
```
[example]
# fragments
_letter = [_A-Za-z]
_digit = [0-9]

# tokens
identifier = {_letter{({_letter}|{_digit})*
number = {_digit}+
other = .
```

This defines a DFA called *example*,
defining two fragments (*_letter* and *_digit*)
and three tokens (*identifier*, *number* and *other*).
Both fragments and tokens are specified as regular expressions.
Fragments are distinguished from tokens because they always
start with an underscore.

### Generating a Python Scanner

We can generate a Python scanner with the command:
```bash
epsilon -o example.py example.epsilon 
```

This creates a standalone python module defining:
- an *Automaton* object named *example*
- a generator function *scan()*

To tokenize a string, we can use the following code:
```python
import example
example.scan(example, string)
```
This generates a sequence of `(token, matching_text)` tuples.
Similarly, we can tokenize from a stream with:
```python
import example
example.scan(example, (c for line in stream for c in line))
```

The module may also be executed directly from the command line,
in which case it will read from the standard input,
emtting tokens on the standard output.

### Generating a Visualisation

We can generate a visualization of the DFA with the commands:
```bash
epsilon -t dot -o example.dot example.epsilon 
dot -Tpng -o example.png example.dot
```
The resulting image is *example.png*,
which may be displayed with the tool of your choice.
Note that *dot* is part of the [GraphViz](https://www.graphviz.org/)
package, which may need to be installed separately.

## Command Line

Basic usage is:
```
epsilon [options] [infile...]
```
The *infiles* are logically concatenated to form the input specification.
If no input files are specified, the specification is taken from standard input.

### Options

| Option | Description |
| ------ | ----------- |
| -h, --help | show help message and exit |
| -t target, --target=target | target language (default = python) |
| -o outfile, --output=outfile | output file (default = standard output) |
| -v, --version | show program's version number and exit |

The currently supported targets are:
- *dot*: generate a dot file
- *execute*: interpret the first DFA defined,
reading from standard input and writing to standard output
- *python*: generate a python scanner


## Input Format

The input specification format follows the
[INI file conventions](https://en.wikipedia.org/wiki/INI_file).
The precise format accepted is described in the
[*configparser* documentation
](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure).
Note that epsilon defines its own interpolation syntax.

Each section, with the execption of *DEFAULTS*, defines exactly one scanner.
Each name in a section specifies either a *fragment* or a *token*.
Fragments always start with an underscore, and tokens never do.

Tokens define the regular expressions which are used to construct the scanner. 
Fragments also define regular expressions, but these are not directly used
in scanner construction.
Instead, thay may be interpolated into other regular expressions.
This supports the reuse of common sub-expressions.

### Interpolation Syntax

Interpolation is invoked by matched braces.
For example "`{_letter}`" is replaced by the definition of *_letter*.
Interpolation may be nested,
and the order of fragment definitions is unimportant. 
Both fragments and tokens may be interpolated.

An open brace may be escaped by preceding it with a backslash, i.e. "`\{`".
In addition, matched braces that can be interpreted as part of the regular
expression are *not* interpolated. This includes repetition counts and
backslash escapes that use braces.

### Regular Expression Syntax

[Regular expressions](https://en.wikipedia.org/wiki/Regular_expression)
specify a pattern that matches input text.
Epsilon interprets both expressions and input text as sequnces of Unicode
codepoints.

Most characters match themselves.
The *metacharacter* "." matches any codepoint.

Metacharacters may be escaped by preceding them with a backslash.
This removes their special meaning.
For instance the expression "\\." only matches the "." character.

#### Character Classes

A character class is a sequence of characters enclosed by square brackets.
This matches matches any character in the class.
For instance, the expression "[abc]" matches "a" or "b" or "c".

Character classes also support ranges, denoted by a "-".
For instance, the expression "[A-Za-z]" matches any
ASCII alphabetical character.

If the first character of a class is "^", the class matches any
character that is not a member.

The only metacharacters in a class are "\\", "-" and "]".
These may be escaped by a preceding backslash.
As a special case, a "]" at the start of a class, or a "-" at the start or end of a class, is treated as escaped.

#### Backslash Escapes

Usually a character escaped by a backslash represents itself.
However, some have a special meaning:

| Escape | Matches |
| ------ | ------- |
| \a | alarm (\x07) |
| \b | backspace (\x08) |
| \e | escape  (\x1b) |
| \f | form feed (\x0c) |
| \n | newline (\x0a) |
| \r | carriage return (\x0d) |
| \t | tab (\x09) |
| \d | any digit character (\p{Nd}) |
| \D | any character not in \d  |
| \h | any horizontal whitespace character ([\x09\x20\xa0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000]) |
| \H | any character not in \h |
| \s | any whitespace character ([\h\v\pZ]) |
| \S | any character not in \s |
| \v | any vertical whitespace character ([\x0a-\x0d\x85\u2028-\u2029]) |
| \V | any character not in \v |
| \w | any word character ([\pL\pN\x5f]) |
| \W | any character not in \w |
| \pX | any character with the single character Unicode general property X |
| \p{X...} | any character with the named Unicode property |
| \PX | any character not in \pX |
| \p{X...} | any character not in \p{X...} |
| \ddd | 1, 2 or 3 octal digit codepoint |
| \o{d...} | 1 or more octal digit codepoint |
| \xhh | 2 hexadecimal digit codepoint |
| \x{h...} | 1 or more hexadecimal digit codepoint |
| \uhhhh | 4 hexadecimal digit codepoint |
| \Uhhhhhhhh | 8 hexadecimal digit codepoint |

#### Quantifiers

An element may be followed by a quantifier:

| Quantifier | Meaning |
| ---------- | ------- |
| ? | zero or one instances |
| * | zero or more instances |
| + | one or more instances |
| {n} | exactly n instances |
| {n,} | n or more instances |
| {n,m} | at least n, and no more than m, instances |

#### Operators

Epsilon supports the following operators, highest precedence first:

| Operator | Meaning |
| -------- | ------- |
| () | grouping |
| &#124; | logical or (alternation) |
| & | logical and |
| ! | complement |
| (implied) | concatenation |

A sequence of elements implies concatenation.

#### Formal Grammar

```
expression = logical_or;
logical_or = logical_and, {'|', logical_and};
logical_and = complement, {'&', complement};
complement = ['!'], concatenation;
    
concatenation = {quantification};
quantification = atom, [quantifier];
quantifier = '?' | '*' | '+' | count;
count = '{', number, [',', [number]], '}';
element = '(', logical_or, ')'
    | '.'
    | class
    | quoted
    | CHARACTER - metachars;
metachars = '|' | '&' | '!' | '?' | '*' | '+' | '{'
    | '(' | ')' | '.' | '[' | '\';
    
class = '[', ['^'], [']' | '-'], {range}, ['-'] ']';
range = member, ['-', member]
member = quoted | class_char;
class_char = CHARACTER - class_metachars;
class_metachars = '\' | '-' | ']';
    
quoted = '\d' | '\D'
    | '\h' | '\H'
    | '\s' | '\S'
    | '\v' | '\V'
    | '\w' | '\W'
    | '\p', CHARACTER | '\P', CHARACTER
    | '\p{', property,  '}' | '\P{', property, '}'
    | '\a' | '\b' | '\e' | '\f' | '\n' | '\r' | '\t'
    | octal_escape
    | hex_escape
    | unicode_escape
    | '\', CHARACTER;
property = {CHARACTER - '}'};
    
octal_escape: '\', octal_digit, [octal_digit, [octal_digit]]
    | '\o{', octal_digit, {octal_digit}, '}';
hex_escape: '\x', 2 * hex_digit
    | '\x{', hex_digit, {hex_digit}, '}';
unicode_escape = '\u', 4 * hex_digit
    | '\U', 8 * hex_digit;
    
octal_digit = '0'..'7';
decimal_digit = '0'..'9';
hex_digit = '0'..'9' | 'A'..'F' | 'a'..'f';
```

## License

Unless noted otherwise, this project (including this manual)
is licensed under the [GPL-3.0](LICENSE/gpl-3.0.txt) license.
