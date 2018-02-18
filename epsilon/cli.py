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

import argparse
import configparser
import collections
import os.path
import re
import sys
from . import dfa
from . import parse
from . import target_dot
from . import target_execute
from . import target_python
from . import version

_targets = collections.OrderedDict([
        ("dot", target_dot.Target),
        ("execute", target_execute.Target),
        ("python", target_python.Target)])

class _Interpolation(configparser.Interpolation):
    _re_braces = re.compile(
            r"(\{[^}]*})"
            r"|\\\{"
            r"|\{[0-9]+(,[0-9]*)}"
            r"|\\[opPx]\{[^}]*}")

    def before_get(self, parser, section, option, value, defaults):
        return self._interpolate(parser, section, option, value, set())

    def _interpolate(self, parser, section, option, value, seen):
        fragments = []
        offset = 0
        while offset < len(value):
            match = self._re_braces.search(value, offset)
            if match:
                start, end = match.span()
                if match.group(1):
                    name = value[start+1:end-1]
                    if name in seen:
                        raise configparser.InterpolationError(name, section,
                                "{}: interpolation loop detected".format(name))
                    interpolated = parser.get(section, name,
                            raw = True, fallback = None)
                    if interpolated is None:
                        raise configparser.InterpolationMissingOptionError(
                                option, section, value, name)
                    fragments.append(value[offset:start])
                    fragments.append(self._interpolate(
                            parser, section, name, interpolated, seen.union({name})))
                    offset = end
                else:
                    fragments.append(value[offset:end])
                    offset = end
            else:
                fragments.append(value[offset:])
                break

        return "".join(fragments)

def _compile(paths, target):
    config = configparser.ConfigParser(interpolation = _Interpolation())
    config.optionxform = str
    if paths:
        for path in paths:
            with open(path) as stream:
                config.read_file(stream)
    else:
        config.read_file(sys.stdin)

    target.emit_header()

    for name in config.sections():
        section = config[name]
        parser = parse.Parser()
        tokens = tuple(key for key in section if not key.startswith("_"))
        if tokens:
            vector = dfa.ExpressionVector(
                    (token, parser.parse(section[token].replace("\n", "")))
                    for token in tokens)
            automaton = dfa.construct(vector)
            target.emit_automaton(name, automaton)

    target.emit_trailer()

def main(argv = sys.argv):
    parser = argparse.ArgumentParser(
            prog = os.path.basename(argv[0]))
    parser.add_argument("-t", "--target",
            choices = _targets,
            default = "python",
            help = "target language (default = python)")
    parser.add_argument("-o", "--output",
            metavar = "outfile",
            nargs = 1,
            help = "output file (default = standard output)")
    parser.add_argument("-v", "--version",
            action = "version",
            version = version.VERSION)
    parser.add_argument("paths", nargs = "*", metavar = "infile")
    args = parser.parse_args(argv[1:])

    target = _targets[args.target](args)
    if args.output:
        with open(args.output[0], "w") as stream:
            with contextlib.redirect_stdout(stream):
                _compile(args.paths, target)
    else:
        _compile(args.paths, target)

if __name__ == '__main__':
    main()
