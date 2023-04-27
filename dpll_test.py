from dpll import dpll
from defns import *
from typing import Set
from hypothesis import given, strategies as st, settings, event

# NOTE: All the tests below are given; you only need to modify `validate_proof`.
#       You may add additional test cases to `test_unit_prop`, `test_sat`, or
#       `test_unsat`.

#########################################
# Normal input/output tests
#########################################

def test_unsat():
    # You may add more tests for UNSATResults, such as manually checking the
    # proof tree that it returns. However, note that there will often be many
    # equally-valid proof trees for a given formula.
    formula = cnf([ [1,2], [-1,2], [1,-2], [-1,-2] ])
    assert isinstance(dpll(formula), UNSATResult)

def test_sat():
    formula = cnf([ [1], [2], [2, 3] ])
    assert isinstance(dpll(formula), SATResult)

#########################################
# Hypothesis PBT
#########################################

# Don't set this very high. Lots of variables to pick from raises the
# probability that a given random clause will be satisfiable, meaning the UNSAT
# case will be less well-tested.
MAX_VAR = 10
MIN_CLAUSE_SIZE = 1
MAX_CLAUSE_SIZE = MAX_VAR
MIN_CLAUSES = 5
MAX_CLAUSES = 200

MAX_EXAMPLES = 5_000  # (Python lets you use underscores for numeric grouping)

# Generators can be complex to write all at once. We've set this stencil up so 
# that you can write a series of smaller generators: first define a generator
# for literals, then clauses, and so on. We've provided the generator for
# literals to help you get started:

# Create a Hypothesis strategy that builds instances of `Literal`, using valid
# variable numbers up to `MAX_VAR`
literals = st.builds(Literal,
                     st.integers(min_value=1, max_value=MAX_VAR),
                     st.booleans())

# Create a Hypothesis strategy that builds instances of `Axiom` using sequences
# (sets, lists, or iterables) of literals, with at least `MIN_CLAUSE_SIZE`
# literals and at most `MAX_CLAUSE_SIZE` literals.
# 
# Use the `unique_by` parameter to create sequences of literals that do not
# contain multiple literals with the same variable number. We don't want clauses
# like `-1 OR 1`. See documentation here:
# https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.lists
axioms = st.builds(Axiom,
                   st.iterables(literals,
                                min_size=MIN_CLAUSE_SIZE,
                                max_size=MAX_CLAUSE_SIZE,
                                unique_by=(lambda l: l.variable)))

# Create a Hypothesis strategy that builds sets of clauses (i.e. formulas) with
# at least `MIN_CLAUSES` clauses and at most `MIN_CLAUSES` clauses.
formulas = st.iterables(axioms,
                        min_size=MIN_CLAUSES,
                        max_size=MAX_CLAUSES).map(frozenset)

@given(formulas)
@settings(deadline=None, max_examples=MAX_EXAMPLES)
def test_pbt(formula: Set[Axiom]):
    result = dpll(formula)

    if result.sat():
        event('sat') # Record a "sat" result for profiling and statistics

        # What properties should a satisfiable result observe? Use `assert` to
        # check these properties.
        #
        # Every clause must have a literal whose sign matches the given
        # assignments.
        assignment_literals = { Literal(v, b)
                                for v, b in result.assignments.items() }
        for clause in formula:
            assert any((l in assignment_literals for l in clause))
    else:
        event('unsat') # Record an "unsat" result for profiling and statistics

        # What properties should an unsatisfiable result observe?
        # (1) The final resolved clause is the empty clause
        assert isinstance(result.clause, Clause)
        assert len(result.clause) == 0

        # (2) The proof itself is valid
        # All validation must happen in the `validate_proof` method
        validate_proof(result.clause, formula)

# NOTE: Do not change the name or parameters of this method, or the autograder
#       will not correctly evaluate your submission!
def validate_proof(clause: Clause, original_formula: Set[Clause]):
    # Recursively validate the proof tree, using `assert` statements.
    # What does it mean for a proof to be valid?
    # (1) It only uses valid axioms
    # (2) All resolved clauses are a valid application of the resolution rule.
    # assert clause in original_formula

    if isinstance(clause, Axiom):
        # What makes an Axiom valid to use in our proof? (FILL)
        assert clause in original_formula

    elif isinstance(clause, ResolvedClause):
        literals = clause.literals
        clause1 = clause.clause1
        clause2 = clause.clause2

        shared = {l.variable for l in clause1 if -l in clause2}
        assert len(shared) ==1
        assert literals == {l for l in clause1.literals| clause2.literals if l.variable not in shared}

        #TODO
        # What makes a ResolvedClause valid in our proof? (FILL)
        validate_proof(clause1, original_formula)
        validate_proof(clause2, original_formula)

    else:
        # NOTE: Our proof tree should not contain Assumptions, so we don't have
        #       a case for that!
        raise Exception(f'Expected ResolvedClause or Axiom, got {clause}')

if __name__ == '__main__':
    test_sat()
    test_unsat()
    test_pbt()
    print("Passes all test!")
