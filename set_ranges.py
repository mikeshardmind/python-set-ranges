"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Michael Hall <https://github.com/mikeshardmind>
"""

# I don't think this should need a license, it's just math, but the law is dumb
# permissive, not super restrrictive license attached

from __future__ import annotations

from collections.abc import Iterator
from functools import reduce
from math import gcd, lcm

_sentinel: int = object()  # type: ignore


def _gen(sr: SetRange) -> Iterator[int]:
    ranges = [range(s.start, s.stop, s.step) for s in sr.ranges]
    current = sr.min_start
    max_stop = sr.max_stop
    step = sr.computed_step

    while current < max_stop:
        if any(current in r for r in ranges):
            yield current
        current += step


class SetRange:
    def __init__(self, s0: int, s1: int=_sentinel, s2: int=_sentinel, /) -> None:

        if s2 is not _sentinel:
            start = s0
            stop = s1
            step = s2
        elif s1 is not _sentinel:
            start = s0
            stop = s1
            step = 1
        else:
            start = 0
            stop = s0
            step = 1

        self.ranges: list[range] = []
        self.min_start = start
        self.max_stop = stop
        self.computed_step = step
        self.ranges.append(range(start, stop, step))

    def __iter__(self) -> Iterator[int]:
        return _gen(self)

    def __and__(self, other: object) -> SetRange:

        if isinstance(other, range):
            r = SetRange.__new__(SetRange)
            r.ranges = [
                range(
                    max(rn.start, other.start),
                    min(rn.stop, other.stop),
                    lcm(rn.step, other.step),
                ) for rn in self.ranges
            ]
            r.min_start = max(self.min_start, other.start)
            r.max_stop = min(self.max_stop, other.stop)
            r.computed_step = lcm(self.computed_step, other.step)
            return r

        if isinstance(other, SetRange):
            return reduce(SetRange.__and__, other.ranges, self)

        return NotImplemented

    def __or__(self, other: object) -> SetRange:

        if isinstance(other, range):
            r = SetRange.__new__(SetRange)
            r.ranges = self.ranges.copy()
            r.ranges.append(other)
            r.min_start = min(self.min_start, other.start)
            r.max_stop = max(self.max_stop, other.stop)
            r.computed_step = gcd(self.computed_step, other.step)
            return r

        if isinstance(other, SetRange):
            r = SetRange.__new__(SetRange)
            return reduce(SetRange.__or__, other.ranges, self)

        return NotImplemented