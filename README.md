# ![εpsilon](logo.png)

Epsilon is a scanner generator.

It converts a sequence of regular expressions into a
[deterministic finite automaton](https://en.wikipedia.org/wiki/Deterministic_finite_automaton).
The DFA accepts input that matches any of these expressions.
Each expression is associated with a token.
The generated scanner applies the DFA repeatedly to input text to 
return a sequence of tokens.

Scanners may be generated for a variety of target languages, including
- Dot (for visualisations)
- Python

Epsilon is currently under heavy development.
It is usable, but probably contains bugs.

## Getting Started

### Prerequisites

You need [Python](https://www.python.org/) 3.6 or later.

### Installing

Epsilon uses [Setuptools](https://en.wikipedia.org/wiki/Setuptools).

To build and install:
```sh
python3 setup.py build
python3 setup.py install
```

You may wish to install under your user account instead
```sh
python3 setup.py install --user
```

### Using

Please see the [epsilon manual](MANUAL.md).

## Contributing

Contributions are very welcome. Please feel free to submit pull requests.

## Versioning

We use [SemVer](http://semver.org/) for versioning.
For the versions available, see the
[tags on this repository](https://github.com/MichaelPaddon/epsilon/tags). 

## Authors

See the list of [authors](AUTHORS) who participated in this project.

## License

Unless noted otherwise, this project is licensed
under the [GPL-3.0](LICENSE/gpl-3.0.txt) license.

Some files, as marked, are licensed under the
[UNICODE, INC. LICENSE AGREEMENT](LICENSE/unicode.txt).

## Acknowledgments

The DFA construction method is an application of
[Brzozowski derivatives](https://en.wikipedia.org/wiki/Brzozowski_derivative).

Epsilon was inspired by and directly based on the paper
[_Owens, S., Reppy, J. and Turon, A., 2009.
Regular-expression derivatives re-examined.
Journal of Functional Programming, 19(2), pp.173-190_
](https://www.cl.cam.ac.uk/~so294/documents/jfp09.pdf).
