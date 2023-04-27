# DO NOT MODIFY THIS FILE

import itertools
from dataclasses import dataclass
from typing import Iterable, Iterator, Set, Union, TypeVar, FrozenSet, Dict

# Please use these classes and helpers in your DPLL code. They have been defined
# as immutable dataclasses to avoid potential errors caused by mutation.

# A `Literal` represents a single literal in a clause. A `Literal` contains its
# variable number (a positive integer) and its sign (a boolean).
#
# For convenience, the negation (-) operator is defined to return the logical
# NOT of a `Literal`. For example:
#
#     > l1 = Literal(1, True)
#     > -l1
#     Literal(variable=1, sign=False)
#
#     > l2 = Literal(1, False)
#     > -l2
#     Literal(variable=2, sign=True)
#
# In addition, when converting a `Literal` to a string with either `print` or
# `str`, it will print as a positive or negative number, depending on its sign:
#
#     > print(Literal(1, True))
#     1
#     > print(Literal(3, False))
#     -3
@dataclass(frozen=True)
class Literal:
    # The literal's variable ID
    variable: int

    # The literal's sign (true or false)
    sign: bool

    def __neg__(self) -> 'Literal':
        return Literal(self.variable, not self.sign)

    def __str__(self) -> str:
        return str(self.variable) if self.sign else f'-{self.variable}'

    def __post_init__(self):
        # Variable IDs must be integers greater than zero
        assert self.variable > 0

# A `Clause` represents some clause, i.e. a set of literals.
#
# In this assignment you will not be creating clauses directly; instead, you
# need to use three types of clauses, each of which is a subclass of `Clause`:
# `Axiom`, `Assumption`, or `ResolvedClause`. When you need to create a clause
# instance, pick the appropriate subclass to use; never create clauses using the
# `Clause` constructor directly.
#
# For convenience, `len` of a clause will return the number of literals it
# contains:
#
#     > clause = Axiom([ Literal(1, True), Literal(2, False) ])
#     > len(clause)
#     2
#
# Also, the `in` operator lets you check whether a Literal is in the set of
# literals for a given Clause:
#
#     > clause = Axiom([ Literal(1, True), Literal(2, False) ])
#     > Literal(1, True) in clause
#     True
#     > Literal(2, True) in clause
#     False
#
# You can also iterate through the literals in a clause by using a `for` loop:
#
#     > clause = Axiom([ Literal(1, True), Literal(2, False) ])
#     > for literal in clause: print(literal)
#     1
#     -2
#
# Finally, converting a Clause to a string with either `str` or `print` will
# show a space-separated list of the given literals:
#
#     > clause = Axiom([ Literal(1, True), Literal(2, False) ])
#     > print(clause)
#     1 -2
#
# NOTE: `ResolvedClause`s and `Assumption`s have slightly different ways of
# printing; see below.
#
@dataclass(frozen=True, init=False)
class Clause:
    # The set of literals contained in this clause
    # (Using a set, rather than a list, to avoid bugs caused by duplication!)
    literals: FrozenSet[Literal]

    def __init__(self, *args):
        raise Exception('Cannot create a Clause directly: '+
                        'Use a ResolvedClause, Axiom, or Assumption instead')

    def __iter__(self) -> Iterator[Literal]:
        return iter(self.literals)

    def __len__(self) -> int:
        return len(self.literals)

    def __contains__(self, literal: Literal) -> bool:
        return literal in self.literals

    def __str__(self) -> str:
        return ' '.join(map(str, self.literals))

# An `Axiom` represents a clause that is given in the original set of formulas;
# i.e. it is an axiom of the given theory.
#
# An `Axiom` is created by passing a list, set, or sequence of Literals:
#
#     > clause = Axiom([ Literal(1, True), Literal(2, 3) ])
#
# NOTE: Since `Axiom` is a subclass of `Clause`, all the convenient features of
# `Clause` apply, like `len(axiom)` and `literal in axiom`.
@dataclass(frozen=True, init=False)
class Axiom(Clause):
    def __init__(self, literals: Iterable[Literal]):
        object.__setattr__(self, 'literals', frozenset(literals))

# An `Assumption` represents a guess that the solver chooses during the process
# of solving a formula. An Assumption clause can only contain a single literal.
#
# An `Assumption` is created by passing the literal that is being assumed:
#
#    > clause = Assumption(Literal(1, True))
#
# Converting an `Assumption` to a string with either `str` or `print` will
# show the literal followed by a "?" to indicate that it is an assumption:
#
#     > print(Assumption(Literal(2, False)))
#     -2?
#
# NOTE: Since `Assumption` is a subclass of `Clause`, all the convenient
# features of `Clause` apply, like `len(assumption)` and `literal in
# assumption`.
#
@dataclass(frozen=True, init=False)
class Assumption(Clause):
    def __init__(self, literal: Literal):
        object.__setattr__(self, 'literals', frozenset([ literal ]))

    def __str__(self) -> str:
        return super().__str__() + '?'

# A `ResolvedClause` represents a clause that has been derived by applying the
# resolution rule to two other clauses (which may be axioms, assumptions, or other resolved clauses).
#
# A `ResolvedClause` is created by passing it a list, set, or sequence of
# literals that the resulting clause contains and the two original clauses:
#
#     > clause1 = Axiom([ Literal(1, True), Literal(2, False) ])
#     > clause2 = Axiom([ Literal(1, False), Literal(3, True) ])
#     > resolved1 = ResolvedClause([ Literal(2, False), Literal(3, True) ],
#                                  clause1, clause2)
#     > assumption = Assumption(Literal(2, True))
#     > resolved2 = ResolvedClause([ Literal(3, True) ], resolved1, assumption)
#
# Converting a ResolvedClause to a string with either `str` or `print` will
# show an ASCII art tree that shows the full proof tree graphically:
#
#     > print(resolved2)
#                 3
#         _______/ \__
#         3 -2      2?
#     ____/ \____
#     1 -2   -1 3
#
# NOTE: Printing ResolvedClauses that are generated in the solver can help you
# debug issues in your implementation!
#
# NOTE: Your tests should check that each instance of a `ResolvedClause` is a
# valid application of resolution.
#
# NOTE: Since `ResolvedClause` is a subclass of `Clause`, all the convenient
# features of `Clause` apply, like `len(resolved)` and `literal in resolved`.
#
@dataclass(frozen=True, init=False)
class ResolvedClause(Clause):
    clause1 : Clause
    clause2 : Clause

    def __init__(self, literals: Iterable[Literal], clause1: Clause, clause2: Clause):
        object.__setattr__(self, 'literals', frozenset(literals))
        object.__setattr__(self, 'clause1', clause1)
        object.__setattr__(self, 'clause2', clause2)

    def __str__(self) -> str:
        # Get an ASCII-art representation of the tree
        lines_1 = str(self.clause1).splitlines()
        lines_2 = str(self.clause2).splitlines()
        line_res = super().__str__()
        if line_res == "":
            line_res = "X"

        width_1 = max(map(len, lines_1))
        width_2 = max(map(len, lines_2))
        width_res = len(line_res)

        JOIN = "/ \\"
        SEP = ' ' * len(JOIN)
        total_width = max(width_1 + len(JOIN) + width_2, width_res)

        bar_1 = len(lines_1[0]) - len(lines_1[0].lstrip())
        bar_2 = len(lines_2[0]) - len(lines_2[0].rstrip())

        if width_1 <= width_2:
            line_res = line_res.center(width_1 * 2 + len(JOIN)).ljust(total_width)
        else:
            line_res = line_res.center(width_2 * 2 + len(JOIN)).rjust(total_width)

        line_sep = ((' ' * bar_1) + '_' * (width_1 - bar_1) + JOIN +
                    ('_' * (width_2 - bar_2) + (' ' * bar_2)))

        return '\n'.join(
            [line_res, line_sep] +
            [l1.rjust(width_1) + SEP + l2.ljust(width_2)
             for (l1, l2) in itertools.zip_longest(lines_1, lines_2, fillvalue='')])

# A `SATResult` is returned whenever the given formula is satisfiable, and contains
# the dictionary that specifies the satisfying variable assignments.
#
# Create a `SATResult` by passing it the dictionary of variable assignments:
#
#     > SATResult({ 1: True, 2: False })
#
@dataclass(frozen=True)
class SATResult:
    assignments: Dict[int, bool]

    def sat(self) -> bool:
        return True

# An `UNSATResult` is returned whenever the given formula is unsatisfiable. The
# `result` should be the empty clause. If you properly manage the proof tree by
# using `ResolvedClause`s, `Axiom`s, and `Assumption`s where appropriate, this
# will be a proof of the empty clause (possibly containing assumptions). When
# the solver has completely shown that no assignment satisfies the formula, the
# final proof of the empty clause should contain no `Assumption`s.
#
# Create an `UNSATResult` by passing the empty clause that you derived:
#
#     > clause1 = Axiom([ Literal(1, True) ])
#     > clause2 = Axiom([ Literal(1, False) ])
#     > resolved = ResolvedClause([], clause1, clause2)
#     > UNSATResult(resolved)
#
# NOTE: Both `SATResult` and `UNSATResult` define the `sat()` method that
# returns a `bool` that indicates whether it is a SAT or UNSAT result.
@dataclass(frozen=True)
class UNSATResult:
    clause: Clause

    def sat(self) -> bool:
        return False

# Helper to make writing tests easier. For example,
#     > cnf([ [1, 2], [-2] ])
# is equivalent to
#     > { Axiom([ Literal(1, True), Literal(2, True) ]),
#         Axiom([ Literal(2, False) ]) }
#
def cnf(list_of_lit_lists: Iterable[Iterable[int]]) -> Set[Clause]:
    return { Axiom({ Literal(abs(l), l > 0) for l in ll })
             for ll in list_of_lit_lists }

# Helper to get the first element of a sequence. For example, it can be used to
# get the first literal in a clause:
#
#     > first(Axiom([ Literal(1, True) ]))
#     Literal(variable=1, sign=True)
#
T = TypeVar('T')
def first(iter: Iterable[T]) -> Union[T, None]:
    for i in iter:
        return i
