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
import collections
import functools
from . import regex
from . import util

Automaton = collections.namedtuple("Automaton",
        ["transitions", "accepts", "error"])

class ExpressionVector(tuple):
    def __new__(cls, iterable):
        return super().__new__(cls, iterable)

    @property
    def NULL(self):
        return self.__class__((name, expr.NULL) for name, expr in self)
    
    def nullable(self):
        return [name for name, expr in self if expr.nullable()]
    
    def derivative(self, symbol):
        return ExpressionVector(
                (name, expr.derivative(symbol)) for name, expr in self)
  
    def derivative_classes(self):
        return filter(None, functools.reduce(util.product_intersections, 
                (expr.derivative_classes() for _, expr in self)))

def construct(expr):
    """Construct an automaton from a regular expression.

    :param expr: a regular expression or a ExpressionVector.
    :return: 
    """
    states = {expr: 0}
    transitions = [[]]

    stack = [expr]
    while stack:
        state = stack.pop()
        number = states[state]
        for derivative_class in state.derivative_classes():
            symbol = derivative_class[0][0]
            nextstate = state.derivative(symbol)
            if nextstate not in states:
                states[nextstate] = len(states)
                transitions.append([])
                stack.append(nextstate)
            
            nextnumber = states[nextstate]
            for first, last in derivative_class:
                transitions[number].append((first, last, nextnumber))
        transitions[number].sort()

    accepts = [state.nullable() for state in states]
    error = states[expr.NULL]
    return Automaton(transitions, accepts, error)

class NoMatchError(Exception):
    def __init__(self, atoms):
        msg = "No match for input {}".format(atoms)
        super().__init__(msg)

def scan(automaton, iterable,
        tosymbol = ord, pack = lambda atoms: "".join(atoms)):
    buffer, offset = [], 0
    state, accept, length = 0, False, 0
    atoms = iterable
    while True:
        if automaton.accepts[state]:
            accept = automaton.accepts[state]
            length = offset

        if offset < len(buffer):
            atom = buffer[offset]
        else:
            atom = next(atoms, None)
            if atom is not None:
                buffer.append(atom)

        if atom is not None:
            symbol = tosymbol(atom)
            transitions = automaton.transitions[state]
            i = bisect.bisect(transitions, (symbol,))
            if i < len(transitions) and symbol == transitions[i][0]:
                state = transitions[i][2]
            elif i > 0 and transitions[i-1][0] <= symbol <= transitions[i-1][1]:
                state = transitions[i-1][2]
            else:
                state = automaton.error
            offset += 1
        else:
            state = automaton.error

        if state == automaton.error:
            if accept:
                yield accept[0], pack(buffer[:length])
                buffer, offset = buffer[length:], 0
                state, accept, length = 0, False, 0
            elif buffer:
                raise NoMatchError(buffer)
            else:
                break
