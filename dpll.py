# Types make Python even MORE fun! But you aren't required to use type
# hints beyond what we provide in the stencil. We use types here to help
# you avoid some common bugs in your DPLL implementation's interface.
from typing import Union, Dict, Set
from defns import *

# Take two proof trees and return the result of applying the resolve rule, which
# results in a proof tree with the original two clauses as branches. Recall the
# resolution rule:
#     A | l    B | -l
#     ---------------
#         A | B
#
# Viewed as a proof tree, this is
#          A B
#       ___/ \____
#       A l   B -l
#
# NOTE: You should only resolve one variable at a time
#
# NOTE: In this assignment `ResolvedClause` requires the set of literals *and*
#       the two clauses that were used as input to generate the resolved clause.
#       This creates a basic proof tree structure.
#
def resolve(c1: Clause, c2: Clause) -> ResolvedClause:
    # Find the variable (or, optionally, set of variables) that should be
    # resolved (FILL)

    res_var = {l.variable for l in c1 if -l in c2}

    # Compute the set of literals in the result (FILL)

    return ResolvedClause((l for l in c1.literals | c2.literals if l.variable not in res_var), c1,c2)

    


# The basic unit propagation algorithm is given in full, except for the
# implementation of `resolve` above.

# Propagate a single decision or inference and return the new formula.
def unit_propagate_literal(formula: Set[Clause], unit: Clause) -> Set[Clause]:
    new_formula: Set[Clause] = set()

    # Get the literal that is being propagated
    if len(unit) != 1:
        raise Exception(f'Trying to propagate non-unit clause: {unit}')
    literal = first(unit)

    # Compute the new set of clauses
    for clause in formula:
        if literal in clause:
            # Clause is satisfied, so we can ignore it
            continue
        elif -literal in clause:
            # Negation is in the clause; this term won't be satisfied so we can
            # remove it from the new clause
            new_formula.add(resolve(clause, unit))
        else:
            # The formula doesn't contain this variable, so we can leave it
            # unchanged
            new_formula.add(clause)

    return new_formula

# Get all the unit clauses in the formula
def get_unit_clauses(formula: Set[Clause]) -> Set[Clause]:
    return { c for c in formula if len(c) == 1 }

# Propagate all unit clauses until no unit clauses are found and return the new
# formula. Add the assignments that are propagated to the assignments dictionary
# (mutated in-place).
def unit_propagate(formula: Set[Clause], assignments: Dict[int, bool]) -> Set[Clause]:
    while True:
        unit_clauses = get_unit_clauses(formula)
        if not unit_clauses:
            break

        for unit in unit_clauses:
            formula = unit_propagate_literal(formula, unit)

            literal = first(unit)
            assignments[literal.variable] = literal.sign

    return formula

# Given a clause (i.e. a proof tree), return a new clause (i.e. proof tree) that
# does not contain any instance of the given assumption. Note that this may
# result in a clause with more literals than the original clause (i.e. it may
# result in a weaker statement).
# 
# Then, when given a proof resulting in an empty clause, this should return
# either a proof of the negation of the assumption (if the assumption was
# necessary for the proof), or another proof of the empty clause (if the
# assumption was not necessary for the given proof).
#
# You may assume that `assumption != clause`.
#
# NOTE: You must re-resolve any resolved clause after you remove the assumption
#       from its children.
#
def remove_assumption(assumption: Assumption, clause: Clause) -> Clause:
    # (FILL)

    if isinstance(clause, Assumption):
        return clause
    
    if isinstance(clause, Axiom):
        return clause
    
    if isinstance(assumption, ResolvedClause):
        if clause.clause1 == assumption:
            return remove_assumption(assumption, clause.clause2)
        elif clause.clause2 == assumption:
            return remove_assumption(assumption, clause.clause1)
        else:
            return resolve(remove_assumption(assumption, clause.clause1),
                           remove_assumption(assumption, clause.clause2))
    else:
        return clause



    

# The core DPLL algorithm is given, except for the implementation of
# `remove_assumption`.

# Pick a variable from the formula
def select_variable(formula: Set[Clause]) -> int:
    for clause in formula:
        for literal in clause:
            return literal.variable
        
# Starts the DPLL solving process, starting with no assignments. (Do not change
# the input arguments or the return type of this method.)
def dpll(formula: Set[Clause]) -> Union[SATResult, UNSATResult]:
    return dpll_internal(formula, {})

def dpll_internal(formula: Set[Clause], assignments: Dict[int, bool]) -> Union[SATResult, UNSATResult]:
    # Run DPLL on a given formula and return a `SATResult` or an `UNSATResult`.

    # Perform unit propagation
    formula = unit_propagate(formula, assignments)

    # If there are no more clauses, return a SATResult
    if not formula:
        return SATResult(assignments)

    # If we have derived the unit clause, return an `UNSATResult` that
    # references one of the empty clause that we have derived. Since
    # ResolvedClauses are proof trees, this will be a proof of the empty clause.
    for clause in formula:
        if len(clause) == 0:
            return UNSATResult(clause)

    # Otherwise, pick a variable to branch on
    branch_on = select_variable(formula)

    # Add this assumption to the formula and try to solve
    true_assumption = Assumption(Literal(branch_on, True))
    true_result = dpll_internal(formula | { true_assumption }, assignments)

    # If we now found a satisfying assignment, return it
    if true_result.sat():
        return true_result

    # If assuming true produces UNSAT, we know that the true assignment is
    # invalid; i.e. the assigning false must be valid or the given formula is
    # UNSAT.
    #
    # Rewrite the proof of the empty clause that we derived when assuming true,
    # but now remove the assumption. This must result in either the empty clause
    # or a proof that our assumption was false (i.e. a proof of the negation of
    # our assumption).

    without_assumption = remove_assumption(true_assumption, true_result.clause)\

    # If it is still a proof of the empty clause, we know that the derivation
    # of the empty clause was not contingent on our assumption, so we can just
    # return this new proof
    #
    # NOTE: This is a taste for how CDCL makes things fast! We can skip trying
    #       the false branch since we know that it will also be UNSAT!
    if len(without_assumption) == 0:
        return UNSATResult(without_assumption)
    
    # Otherwise, we have derived a proof of the opposite of our assumption, so
    # we can now add it directly to the list of formulas and continue solving.
    false_result = dpll_internal(formula | { without_assumption }, assignments)

    # Either the false result is SAT, or the given formula is UNSAT. In either
    # case, we just return the result.
    return false_result
