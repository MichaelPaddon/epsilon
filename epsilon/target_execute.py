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

import sys
from . import dfa
from . import target

class Target(target.Target):
    def __init__(self, args):
        super().__init__(args)
        self._automata = []

    def emit_automaton(self, name, automaton):
        self._automata.append(automaton)

    def emit_trailer(self):
        if self._automata:
            text = (c for line in sys.stdin for c in line)
            for token, match in dfa.scan(self._automata[0], text):
                print(token, repr(match))

