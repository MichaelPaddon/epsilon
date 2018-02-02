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

import random
import unittest
from . import parse

class TestIntegerSet(unittest.TestCase):
    ITERATIONS = 1000
    RANGE = 100
    SAMPLES = 50

    PATTERNS = [
        ("", "Epsilon()"),
        ("a", "SymbolSet(((97, 97),))"),
        ("abc", "Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((98, 98),)), SymbolSet(((99, 99),))))"),
        ("a|b", "SymbolSet(((97, 98),))"),
        ("a&b", "LogicalAnd(SymbolSet(((98, 98),)), SymbolSet(((97, 97),)))"),
        ("!a", "SymbolSet(((0, 96), (98, 1114111)))"),
        ("a?", "LogicalOr(SymbolSet(((97, 97),)), Epsilon())"),
        ("a+", "Concatenation(SymbolSet(((97, 97),)), KleeneClosure(SymbolSet(((97, 97),))))"),
        ("a*", "KleeneClosure(SymbolSet(((97, 97),)))"),
        ("a{3}", "Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), SymbolSet(((97, 97),))))"),
        ("a{3,}", "Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), KleeneClosure(Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), SymbolSet(((97, 97),))))))))"),
        ("a{3,5}", "Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), Concatenation(LogicalOr(Epsilon(), Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), SymbolSet(((97, 97),))))), LogicalOr(Epsilon(), Concatenation(SymbolSet(((97, 97),)), Concatenation(SymbolSet(((97, 97),)), SymbolSet(((97, 97),)))))))))"),
        ("a*|b*", "LogicalOr(KleeneClosure(SymbolSet(((98, 98),))), KleeneClosure(SymbolSet(((97, 97),))))"),
        ("a*&b*", "LogicalAnd(KleeneClosure(SymbolSet(((98, 98),))), KleeneClosure(SymbolSet(((97, 97),))))"),
        ("(ab*)", "Concatenation(SymbolSet(((97, 97),)), KleeneClosure(SymbolSet(((98, 98),))))"),
        ("[]a-z0-9-]", "SymbolSet(((45, 45), (48, 57), (93, 93), (97, 122)))"),
        ]

    def test_patterns(self):
        parser = parse.Parser()
        for pattern, expected in self.PATTERNS:
            expr = parser.parse(pattern)
            self.assertEqual(str(expr), expected)

if __name__ == '__main__':
    unittest.main()
