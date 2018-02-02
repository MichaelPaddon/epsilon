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
from . import util

class TestIntegerSet(unittest.TestCase):
    ITERATIONS = 1000
    RANGE = 100
    SAMPLES = 50

    def test_construction(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            x = util.IntegerSet(a)
            self.assertEqual(util.IntegerSet(x), x)
            self.assertEqual(x.cardinality(), len(a))

    def test_has(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            x = util.IntegerSet(a)
            self.assertFalse(x.has(-1))
            self.assertFalse(x.has(self.RANGE + 1))
            for j in range(self.RANGE):
                self.assertEqual(j in a, x.has(j))

    def test_subset(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            x = util.IntegerSet(a)
            y = util.IntegerSet(random.sample(a, self.SAMPLES - 1))
            self.assertTrue(x.issubset(x))
            self.assertTrue(y.issubset(x))
            self.assertFalse(x.issubset(y))
            self.assertFalse(x.issubset([]))

    def test_superset(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            x = util.IntegerSet(a)
            y = util.IntegerSet(random.sample(a, self.SAMPLES - 1))
            self.assertTrue(x.issuperset(x))
            self.assertTrue(x.issuperset(y))
            self.assertFalse(y.issuperset(x))
            self.assertTrue(x.issuperset([]))

    def test_disjoint(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            b = set(random.sample(range(self.RANGE), self.SAMPLES))
            x = util.IntegerSet(a)
            y = util.IntegerSet(b)
            self.assertEqual(a.isdisjoint(b), x.isdisjoint(y))
            self.assertTrue(x.isdisjoint([]))

    def test_union(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            b = set(random.sample(range(self.RANGE), self.SAMPLES))
            c = a | b
            x = util.IntegerSet(a).union(b)
            self.assertEqual(x, util.IntegerSet(b).union(a))
            self.assertEqual(x, util.IntegerSet(c))

    def test_intersection(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            b = set(random.sample(range(self.RANGE), self.SAMPLES))
            c = a & b
            x = util.IntegerSet(a).intersection(b)
            self.assertEqual(x, util.IntegerSet(b).intersection(a))
            self.assertEqual(x, util.IntegerSet(c))

    def test_difference(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            b = set(random.sample(range(self.RANGE), self.SAMPLES))
            c = a - b
            x = util.IntegerSet(a).difference(b)
            self.assertEqual(x, util.IntegerSet(c))

    def test_symmetric_difference(self):
        for i in range(self.ITERATIONS):
            a = set(random.sample(range(self.RANGE), self.SAMPLES))
            b = set(random.sample(range(self.RANGE), self.SAMPLES))
            c = a ^ b
            x = util.IntegerSet(a).symmetric_difference(b)
            self.assertEqual(x, util.IntegerSet(b).symmetric_difference(a))
            self.assertEqual(x, util.IntegerSet(c))

if __name__ == '__main__':
    unittest.main()
