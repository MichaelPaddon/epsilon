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
identifier = <_letter>(<_letter>|<_digit>)*
number = <_digit>+
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

Interpolation is invoked by angle brackets.
For example "`<_letter>`" is replaced by the definition of *_letter*.
Interpolation may be nested,
and the order of fragment definitions is unimportant. 
Both fragments and tokens may be interpolated.

If you want to use an an open angled bracket in your expression,
escape it with a backslash, i.e. "`\<`".

### Regular Expression Syntax

The regular expressions accepted are specified by the following grammar:
```
expression = logical_or;
logical_or = logical_and, {'|', logical_and};
logical_and = complement, {'&', complement};
complement = ['!'], concatenation;
    
concatenation = {quantification};
quantification = element, [quantifier];
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
