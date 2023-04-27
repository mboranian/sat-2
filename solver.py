# DO NOT MODIFY THIS FILE
# This file is set up to be executable as a script, and enable DIMACS
# format I/O. It calls your DPLL solution in dpll.py.

# Run the solver with `python3 solver.py <file.cnf>` (or, if you are on Windows,
# `python solver.py <file.cnf>`)
#
# Display proofs of unsatisfiability by specifying `--proof`, e.g.
# `python3 solver.py --proof <file.cnf>`

import argparse
from dpll import dpll
from typing import Dict
from defns import *

# Read and parse a cnf file, returning the variable set and clause set
def read_input(cnf_file: str):
    with open(cnf_file, 'r') as f:
        tokens = [int(tok) for line in f.readlines()
                  if line[0] != 'p' and line[0] != 'c'
                  for tok in line.strip().split()]

    # Split into clauses delimited by 0
    # Allow a trailing clause without a terminator
    i = 0
    while i < len(tokens):
        try:
            n = tokens.index(0, i)
        except ValueError:
            n = len(tokens)
        yield tokens[i:n]
        i = n + 1

# Format the result in DIMACS format
def get_dimacs(assignment: Dict[int, bool]) -> str:
    return ' '.join([str(var if value else -var)
                     for var, value in assignment.items()])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-p', '--proof', help='display proof tree when UNSAT',
                        action='store_true')

    args = parser.parse_args()
    formula = cnf(read_input(args.input))
    result = dpll(formula)
    if result.sat():
        print('s SATISFIABLE')
        print(get_dimacs(result.assignments))
    else:
        print('s UNSATISFIABLE')
        if args.proof:
            print(result.clause)
