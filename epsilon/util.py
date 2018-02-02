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

def product_intersections(*sets):
    """Return the intersections of the cartesian product of sequences of sets.

    :param sets: Iterables sof sets.
    :return: A set of intersections.
    """
    return set(x[0].intersection(*x[1:]) for x in itertools.product(*sets))

class IntegerSet(tuple):
    """An immutable set of integers, represented as sorted tuple of disjoint,
    non-contiguous ranges.
    """

    def __new__(cls, iterable = ()):
        """Return a new set of integers.

        :param iterable: an iterable of integers or integer ranges.
        A range is a two valued sequence, specifying the first and
        last integers of a contiguous segment. If first is greater than
        last, the range is treated as empty.
        A bare integer, x, represents the range (x, x).
        """

        def canonical(iterable):
            ranges = sorted(filter(lambda r: r[0] <= r[1],
                    ((x, x) if isinstance(x, int) else (int(x[0]), int(x[1]))
                        for x in iterable)))
            if ranges:
                r = ranges[0]
                for s in ranges[1:]:
                    if s[0] > r[1] + 1:
                        yield r
                        r = s
                    else:
                        r = (r[0], max(r[1], s[1]))
                yield r

        if isinstance(iterable, cls):
            self = super().__new__(cls, iterable)
        else:
            self = super().__new__(cls, canonical(iterable))
        return self

    def has(self, x):
        """Test for set membership.

        :param x: an integer
        :return: True if the integer is a member of the set.
        """
        i = bisect.bisect(self, (x,))
        return (i < len(self) and x == self[i][0])\
                or (i > 0 and self[i-1][0] <= x <= self[i-1][1])

    def cardinality(self):
        """Return the number of integers in the set."""
        return functools.reduce(lambda l, r: l + r[1] - r[0] + 1, self, 0)

    def isdisjoint(self, other):
        """Return True if the set has no integers in common with other."""
        return not self.intersection(other)

    def issubset(self, other):
        """Test whether every integer in the set is in other."""
        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        i = iter(other)
        r = next(i, None)
        for s in self:
            while r and r[1] < s[0]:
                r = next(i, None)
            if not r or s[0] < r[0] or s[1] > r[1]:
                return False
        return True

    def issuperset(self, other):
        """Test whether every integer in other is in the set."""
        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        i = iter(self)
        r = next(i, None)
        for s in other:
            while r and r[1] < s[0]:
                r = next(i, None)
            if not r or s[0] < r[0] or s[1] > r[1]:
                return False
        return True

    def union(self, *others):
        """Return a new set with integers from the set and all others."""
        return self.__class__(itertools.chain(self, *others))

    def intersection(self, *others):
        """Return a new set with integers common to the set and all others."""
        intersection = self
        for other in others:
            if not isinstance(other, self.__class__):
                other = self.__class__(other)

            ranges = []
            i, j = iter(intersection), iter(other)
            r, s = next(i, None), next(j, None)
            while r and s:
                x, y = max(r[0], s[0]), min(r[1], s[1])
                if x <= y:
                    ranges.append((x, y))
                r = r if r[1] > y else next(i, None)
                s = s if s[1] > y else next(j, None)
            intersection = self.__class__(ranges)
        return intersection

    def difference(self, *others):
        """Return a new set with integers in the set but not in the others."""
        difference = self
        for other in others:
            if not isinstance(other, self.__class__):
                other = self.__class__(other)

            ranges = []
            i, j = iter(difference), iter(other)
            r, s = next(i, None), next(j, None)
            while r:
                if s:
                    if r[0] > s[1]:
                        s = next(j, None)
                    elif r[1] < s[0]:
                        ranges.append(r)
                        r = next(i, None)
                    else:
                        if r[0] < s[0]:
                            ranges.append((r[0], s[0] - 1))
                        if r[1] > s[1]:
                            r = (s[1] + 1, r[1])
                            s = next(j, None)
                        else:
                            r = next(i, None)
                else:
                    ranges.append(r)
                    r = next(i, None)
            difference = self.__class__(ranges)
        return difference

    def symmetric_difference(self, other):
        """Return a new set with integers in either the set or other,
        but not both.
        """
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.difference(other).union(other.difference(self))
