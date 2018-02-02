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

import bisect
import functools
import itertools
from . import util

def expressions(codespace):
    codespace = util.IntegerSet(codespace)

    @functools.total_ordering
    class Expression:
        def __eq__(self, expr):
            return self._orderby() == expr._orderby()
    
        def __lt__(self, expr):
            return self._orderby() < expr._orderby()
    
        def __hash__(self):
            return hash(self._orderby())
    
        def __repr__(self):
            return "<{}>".format(str(self))
    
        def nullable(self):
            nu = self.nu()
            assert nu == self.EPSILON or nu == self.NULL
            return nu == self.EPSILON
    
    class SymbolSet(Expression):
        def __init__(self, codepoints = ()):
            self._codepoints = util.IntegerSet(codepoints)
            if not codespace.issuperset(self._codepoints):
                raise ValueError("code point out of range")
    
        def __repr__(self):
            return "{}({})".format(self.__class__.__name__,
                    self._codepoints or "")
    
        def _orderby(self):
            return self.__class__.__name__, self._codepoints
    
        @property
        def codepoints(self):
            return self._codepoints
    
        def nu(self):
            return self.NULL
    
        def derivative(self, symbol):
            return self.EPSILON if self._codepoints.has(symbol) else self.NULL
    
        def derivative_classes(self):
            return {self._codepoints, codespace.difference(self._codepoints)}
    
    class Epsilon(Expression):
        def __repr__(self):
            return "{}()".format(self.__class__.__name__)
    
        def _orderby(self):
            return self.__class__.__name__,
    
        def nu(self):
            return self
    
        def derivative(self, symbol):
            return self.NULL
    
        def derivative_classes(self):
            return {codespace}
    
    class KleeneClosure(Expression):
        def __new__(cls, expr):
            if isinstance(expr, KleeneClosure):
                return expr
            elif expr == cls.EPSILON:
                return expr
            elif expr == cls.NULL:
                return cls.EPSILON
    
            self = super().__new__(cls)
            self._expr = expr
            return self
    
        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, self._expr)
    
        def _orderby(self):
            return self.__class__.__name__, self._expr
    
        def nu(self):
            return self.EPSILON
    
        def derivative(self, symbol):
            return Concatenation(self._expr.derivative(symbol), self)
    
        def derivative_classes(self):
            return self._expr.derivative_classes()
    
    class Complement(Expression):
        def __new__(cls, expr):
            if isinstance(expr, Complement):
                return expr._expr
            elif isinstance(expr, SymbolSet):
                return SymbolSet(codespace.difference(expr.codepoints))
    
            self = super().__new__(cls)
            self._expr = expr
            return self
    
        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, self._expr)
    
        def _orderby(self):
            return self.__class__.__name__, self._expr
    
        def nu(self):
            nu = self._expr.nu()
            assert nu == self.EPSILON or nu == self.NULL
            return self.NULL if nu == self.EPSILON else self.EPSILON
    
        def derivative(self, symbol):
            return Complement(self._expr.derivative(symbol))
    
        def derivative_classes(self):
            return self._expr.derivative_classes()
    
    class Concatenation(Expression):
        def __new__(cls, left, right):
            if isinstance(left, Concatenation):
                left, right = left._left, Concatenation(left._right, right)
    
            if left == cls.NULL:
                return left
            elif right == cls.NULL:
                return right
            elif left == cls.EPSILON:
                return right
            elif right == cls.EPSILON:
                return left
    
            self = super().__new__(cls)
            self._left = left
            self._right = right
            return self
    
        def __repr__(self):
            return "{}({}, {})".format(self.__class__.__name__,
                    self._left, self._right)
    
        def _orderby(self):
            return self.__class__.__name__, self._left, self._right
    
        def nu(self):
            return LogicalAnd(self._left.nu(), self._right.nu())
    
        def derivative(self, symbol):
            return LogicalOr(
                    Concatenation(self._left.derivative(symbol), self._right),
                    Concatenation(self._left.nu(),
                        self._right.derivative(symbol)))
    
        def derivative_classes(self):
            return self._left.derivative_classes() if not self._left.nullable()\
                    else filter(None, util.product_intersections(
                        self._left.derivative_classes(),
                        self._right.derivative_classes()))
    
    class LogicalOr(Expression):
        def __new__(cls, left, right):
            if isinstance(left, SymbolSet) and isinstance(right, SymbolSet):
                return SymbolSet(left.codepoints.union(right.codepoints))
    
            terms = set() 
            stack = [left, right]
            while stack:
                expr = stack.pop()
                if isinstance(expr, cls):
                    stack.append(expr._left)
                    stack.append(expr._right)
                elif expr == cls.NULL:
                    pass
                elif expr == cls.SIGMA:
                    return expr
                else:
                    terms.add(expr)
    
            if not terms:
                return cls.NULL
    
            new = super().__new__
            def construct(left, right):
                self = new(cls)
                self._left, self._right = left, right
                return self
            return functools.reduce(construct, sorted(terms, reverse = True))
    
        def __repr__(self):
            return "{}({}, {})".format(self.__class__.__name__,
                    self._left, self._right)
    
        def _orderby(self):
            return self.__class__.__name__, self._left, self._right
    
        def nu(self):
            return LogicalOr(self._left.nu(), self._right.nu())
    
        def derivative(self, symbol):
            return LogicalOr(
                    self._left.derivative(symbol),
                    self._right.derivative(symbol))
    
        def derivative_classes(self):
            return filter(None, util.product_intersections(
                    self._left.derivative_classes(),
                    self._right.derivative_classes()))
    
    class LogicalAnd(Expression):
        def __new__(cls, left, right):
            terms = set() 
            stack = [left, right]
            while stack:
                expr = stack.pop()
                if isinstance(expr, cls):
                    stack.append(expr._left)
                    stack.append(expr._right)
                elif expr == cls.NULL:
                    return expr
                elif expr == cls.SIGMA:
                    pass
                else:
                    terms.add(expr)
    
            if not terms:
                return cls.SIGMA
    
            new = super().__new__
            def construct(left, right):
                self = new(cls)
                self._left, self._right = left, right
                return self
            return functools.reduce(construct, sorted(terms, reverse = True))
    
        def __repr__(self):
            return "{}({}, {})".format(self.__class__.__name__,
                    self._left, self._right)
    
        def _orderby(self):
            return self.__class__.__name__, self._left, self._right
    
        def nu(self):
            return LogicalAnd(self._left.nu(), self._right.nu())
    
        def derivative(self, symbol):
            return LogicalAnd(
                    self._left.derivative(symbol),
                    self._right.derivative(symbol))
    
        def derivative_classes(self):
            return filter(None, util.product_intersections(
                    self._left.derivative_classes(),
                    self._right.derivative_classes()))

        Expression.EPSILON = Epsilon()
        Expression.NULL = SymbolSet()
        Expression.SIGMA = SymbolSet(codespace)

    return type("Regex", (object,), locals())

unicode = expressions(((0, 0x10ffff),))
