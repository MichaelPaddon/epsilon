# Epsilon
# Copyright (C) 2018
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import functools
import itertools
from . import regex
from . import ucd
from . import util

class SyntaxError(Exception):
    """Thrown on a regular expression syntax error."""

class _Buffer(list):
    """Parsing input buffer."""

    def __init__(self, iterable):
        super().__init__(reversed(iterable))

    def read(self):
        return self.pop() if self else ""

    def peek(self):
        return self[-1] if self else ""

    def push(self, c):
        if c:
            self.append(c)

    def readwhile(self, predicate, count = None):
        consumed = []
        if count is None:
            while self and predicate(self[-1]):
                consumed.append(self.pop())
        else:
            while self and count > 0 and predicate(self[-1]):
                consumed.append(self.pop())
                count -= 1
        return "".join(consumed)

    def expect(self, wanted):
        for c in wanted:
            if self.read() != c:
                raise SyntaxError("'{}' expected".format(wanted))
        return wanted

def _unicode_property_codepoints(name):
    """Return the codepoints comprising a unicode property.

    :param name: the name of a property
    :return: an IntegerSet of codepoints
    """
    if len(name) == 1:
        keys = [k for k in ucd.general_categories if k.startswith(name)]
        if not keys:
            raise SyntaxError("unknown unicode category '{}'".format(name))
        elements = itertools.chain.from_iterable(
                [ucd.general_categories[k] for k in keys])
    elif name == "L&":
        elements = itertools.chain(
                ucd.general_categories["Lu"],
                ucd.general_categories["Ll"],
                ucd.general_categories["Lt"])
    elif name in ucd.general_categories:
        elements = ucd.general_categories[name]
    else:
        raise SyntaxError("unknown unicode property '{}'".format(name))
    return util.IntegerSet(elements)

class Parser:
    r"""A regular expression parser.

    The regular expressions accepted are specified by this grammar:

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
    """

    def parse(self, iterable):
        buffer = _Buffer(iterable)
        expr = self._parse_logical_or(buffer)
        if buffer:
            raise SyntaxError("'{}' unexpected".format(buffer.read()))
        return expr

    _metacharacters = frozenset(r"\.[|&!()?*+{")
    _octal_digits = frozenset("01234567")
    _decimal_digits = frozenset("0123456789")
    _hex_digits = frozenset("0123456789ABCDEFabcdef")

    _horizontal_space = util.IntegerSet(
            (0x09, 0x20, 0xa0, 0x1680, 0x180e,
            (0x2000, 0x200a), 0x202f, 0x205f, 0x3000))
    _vertical_space = util.IntegerSet(
            ((0x0a, 0x0d), 0x85, 0x2028, 0x2029))

    _escapes = {
        "a": util.IntegerSet((0x07,)),
        "b": util.IntegerSet((0x08,)),
        "e": util.IntegerSet((0x1b,)),
        "f": util.IntegerSet((0x0c,)),
        "n": util.IntegerSet((0x0a,)),
        "r": util.IntegerSet((0x0d,)),
        "t": util.IntegerSet((0x09,)),
        "d": util.IntegerSet(ucd.general_categories["Nd"]),
        "h": _horizontal_space,
        "s": util.IntegerSet(itertools.chain(
            _unicode_property_codepoints("Z"),
            _horizontal_space,
            _vertical_space)),
        "v": _vertical_space,
        "w": util.IntegerSet(itertools.chain(
            _unicode_property_codepoints("L"),
            _unicode_property_codepoints("N"),
            (0x5f,)))}
    _escapes["D"] = regex.unicode.codespace.difference(_escapes["d"])
    _escapes["H"] = regex.unicode.codespace.difference(_escapes["h"])
    _escapes["S"] = regex.unicode.codespace.difference(_escapes["s"])
    _escapes["V"] = regex.unicode.codespace.difference(_escapes["v"])
    _escapes["W"] = regex.unicode.codespace.difference(_escapes["w"])

    def _parse_logical_or(self, buffer):
        expr = self._parse_logical_and(buffer)
        c = buffer.read()
        while c == '|':
            right = self._parse_logical_and(buffer)
            expr = regex.unicode.LogicalOr(expr, right)
            c = buffer.read()
        else:
            buffer.push(c)
        return expr

    def _parse_logical_and(self, buffer):
        expr = self._parse_complement(buffer)
        c = buffer.read()
        while c == '&':
            right = self._parse_complement(buffer)
            expr = regex.unicode.LogicalAnd(expr, right)
            c = buffer.read()
        else:
            buffer.push(c)
        return expr

    def _parse_complement(self, buffer):
        complement = False
        c = buffer.read()
        if c == "!":
            complement = True
        else:
            buffer.push(c)
        expr = self._parse_concatenation(buffer)
        return regex.unicode.Complement(expr) if complement else expr

    def _parse_concatenation(self, buffer):
        expr = regex.unicode.Epsilon()
        while buffer:
            length = len(buffer)
            right = self._parse_quantification(buffer)
            if length == len(buffer):
                break
            expr = regex.unicode.Concatenation(expr, right)
        return expr

    def _parse_quantification(self, buffer):
        expr = self._parse_element(buffer)
        c = buffer.read()
        if c == "?":
            expr = regex.unicode.LogicalOr(expr, regex.unicode.Epsilon())
        elif c == "*":
            expr = regex.unicode.KleeneClosure(expr)
        elif c == "+":
            expr = regex.unicode.Concatenation(expr,
                    regex.unicode.KleeneClosure(expr))
        elif c == "{":
            mincount, maxcount = self._parse_count(buffer)
            expr = functools.reduce(
                    lambda x, y: regex.unicode.Concatenation(x, y),
                    itertools.repeat(expr, mincount),
                    regex.unicode.Epsilon())
            if maxcount is None:
                expr = regex.unicode.Concatenation(expr,
                        regex.unicode.KleeneClosure(expr))
            else:
                expr = functools.reduce(
                        lambda x, y: regex.unicode.Concatenation(x,
                            regex.unicode.LogicalOr(expr,
                                regex.unicode.Epsilon())),
                        itertools.repeat(expr, maxcount - mincount),
                        expr)
        else:
            buffer.push(c)
        return expr

    def _parse_count(self, buffer):
        # open brace already consumed
        digits = buffer.readwhile(lambda x: x in self._decimal_digits)
        if len(digits) == 0:
            raise SyntaxError("decimal digit expected")
        mincount = int(digits)

        c = buffer.read()
        if c == ",":
            digits = buffer.readwhile(lambda x: x in self._decimal_digits)
            if len(digits):
                maxcount = int(digits)
                if maxcount < mincount:
                    raise SyntaxError("maximum count must be >= minimum count")
            else:
                maxcount = None
            buffer.expect("}")
        elif c == "}":
            maxcount = mincount
        else:
            raise SyntaxError("'}' expected")
        return mincount, maxcount

    def _parse_element(self, buffer):
        """Return an element expression."""
        c = buffer.read()
        if c == "(":
            expr = self._parse_logical_or(buffer)
            buffer.expect(")")
        elif c == ".":
            expr = regex.unicode.SymbolSet(regex.unicode.codespace)
        elif c == "[":
            expr = self._parse_class(buffer)
        elif c == "\\":
            expr = regex.unicode.SymbolSet(self._parse_quote(buffer))
        elif c not in self._metacharacters:
            expr = regex.unicode.SymbolSet([ord(c)])
        else:
            expr = regex.unicode.Epsilon()
            buffer.push(c)
        return expr

    def _parse_class(self, buffer):
        """Return a SymbolSet expression."""
        # open bracket already consumed
        members = []
        complement = False

        c = buffer.read()
        if c == "^":
            complement = True
            c = buffer.read()

        if c == "-" or c == "]":
            members.append(util.IntegerSet([ord(c)]))
            c = buffer.read()

        while c != "-" and c!= "]":
            buffer.push(c)
            members.append(self._parse_range(buffer))
            c = buffer.read()

        if c == "-":
            members.append(util.IntegerSet([ord(c)]))
            c = buffer.read()
            if c != "]":
                raise SyntaxError("bad range")

        if c != "]":
            raise SyntaxError("']' expected")

        codepoints = util.IntegerSet(itertools.chain.from_iterable(members))
        if complement:
            codepoints = regex.unicode.codespace.difference(codepoints)
        return regex.unicode.SymbolSet(codepoints)

    def _parse_range(self, buffer):
        """Return an IntegerSet of codepoints."""
        first = self._parse_member(buffer)
        c = buffer.read()
        if c == "-" and buffer.peek() not in "-]":
            if first.cardinality() != 1:
                raise SyntaxError("start of range must be a single character")
            last = self._parse_member(buffer)
            if last.cardinality() != 1:
                raise SyntaxError("end of range must be a single character")
            return util.IntegerSet([(first[0][0], last[0][0])])
        else:
            buffer.push(c)
            return first

    def _parse_member(self, buffer):
        """Return an IntegerSet of codepoints."""
        c = buffer.read()
        if c == "\\":
            return self._parse_quote(buffer)
        elif c: 
            assert c not in "-]"
            return util.IntegerSet((ord(c),))
        else:
            raise SyntaxError("']' expected")

    def _parse_quote(self, buffer):
        """Return an IntegerSet of codepoints."""
        # backslash already consumed
        c = buffer.read()
        if c in self._escapes:
            return self._escapes[c]
        elif c == "p":
            c = buffer.read()
            if c == "{":
                name = buffer.readwhile(lambda x: x != "}")
                buffer.expect("}")
                return _unicode_property_codepoints(name)
            elif c:
                return _unicode_property_codepoints(c)
            else:
                raise SyntaxError("property name expected")
        elif c == "P":
            c = buffer.read()
            if c == "{":
                name = buffer.readwhile(lambda x: x != "}")
                buffer.expect("}")
                return regex.unicode.codespace.difference(
                        _unicode_property_codepoints(name))
            elif c:
                return regex.unicode.codespace.difference(
                        _unicode_property_codepoints(c))
            else:
                raise SyntaxError("property name expected")
        elif c in self._octal_digits:
            digits = c + buffer.readwhile(
                    lambda x: x in self._octal_digits, 2)
            codepoint = int(digits, 8)
            if regex.unicode.codespace.has(codepoint):
                return util.IntegerSet((codepoint,))
            raise SyntaxError("\\{}: codepoint out of range".format(digits))
        elif c == "o":
            buffer.expect("{")
            digits = buffer.readwhile(lambda x: x in self._octal_digits)
            if len(digits) < 1:
                raise SyntaxError("octal digit expected")
            buffer.expect("}")
            codepoint = int(digits, 8)
            if regex.unicode.codespace.has(codepoint):
                return util.IntegerSet((codepoint,))
            raise SyntaxError(
                    "\\o{{{}}}: codepoint out of range".format(digits))
        elif c == "x":
            c = buffer.read()
            if c == "{":
                digits = buffer.readwhile(lambda x: x in self._hex_digits)
                if len(digits) < 1:
                    raise SyntaxError("hex digit expected")
                buffer.expect("}")
            elif c in self._hex_digits:
                digits = c + buffer.readwhile(
                        lambda x: x in self._hex_digits, 1)
                if len(digits) != 2:
                    raise SyntaxError("exactly 2 hex digits expected")
            codepoint = int(digits, 16)
            if regex.unicode.codespace.has(codepoint):
                return util.IntegerSet((codepoint,))
            print(codepoint, regex.unicode.codespace)
            raise SyntaxError(
                    "\\x{{{}}}: codepoint out of range".format(digits))
        elif c == "u":
            digits = buffer.readwhile(lambda x: x in self._hex_digits, 4)
            if len(digits) != 4:
                raise SyntaxError("exactly 4 hex digits expected")
            codepoint = int(digits, 16)
            if regex.unicode.codespace.has(codepoint):
                return util.IntegerSet((codepoint,))
            raise SyntaxError("\\u{}: codepoint out of range".format(digits))
        elif c == "U":
            digits = buffer.readwhile(lambda x: x in self._hex_digits, 8)
            if len(digits) != 8:
                raise SyntaxError("exactly 8 hex digits expected")
            codepoint = int(digits, 16)
            if regex.unicode.codespace.has(codepoint):
                return util.IntegerSet((codepoint,))
            raise SyntaxError("\\U{}: odepoint out of range".format(digits))
        elif c:
            return util.IntegerSet((ord(c),))
        else:
            raise SyntaxError("character expected after '\\'")
