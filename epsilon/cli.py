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
    def before_get(self, parser, section, option, value, defaults):
        return self._interpolate(parser, section, option, value, 1)

    def _interpolate(self, parser, section, option, value, depth):
        if depth > configparser.MAX_INTERPOLATION_DEPTH:
            raise configparser.InterpolationDepthError(option, section, value)
        fragments = []
        escape = False
        start = offset = 0
        while offset < len(value):
            if escape:
                escape = False
                offset += 1
            elif value[offset] == "\\":
                escape = True
                offset += 1
            elif value[offset] == "<":
                if start < offset:
                    fragments.append(value[start:offset])
                offset += 1
                end = value.find(">", offset)
                if end < 0:
                    msg = "Unterminated interpolation: "\
                            "option {!r} in section {!r} is missing a '>'. "\
                            "Raw value: {!r}".format(option, section, value)
                    raise configparser.InterpolationSyntaxError(
                            option, section, msg)
                name = value[offset:end]
                rawvalue = parser.get(section, name,
                        raw = True, fallback = None)
                if rawvalue is None:
                    raise configparser.InterpolationMissingOptionError(
                            option, section, value, name)
                interpolated = self._interpolate(
                        parser, section, option, rawvalue, depth + 1)
                if interpolated:
                    fragments.append(interpolated)
                start = offset = end + 1
            else:
                offset += 1
        if start < offset:
            fragments.append(value[start:offset])
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
