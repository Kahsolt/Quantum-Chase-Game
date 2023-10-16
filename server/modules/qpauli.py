#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/15

# about Pauli operator and Pauli strings

from functools import reduce

from modules.xrand import random_float, random_int
from modules.utils import *

PauliTerm = Tuple[float, str]
PauliMat = ndarray
HamMat = ndarray
HamConst = float
Ham = Tuple[HamMat, HamConst]

def_gate = lambda mat: np.asarray(mat, dtype=np.complex64)

PAULI_MATRIX = {
  'I': def_gate([
    [1, 0],
    [0, 1],
  ]),
  'X': def_gate([
    [0, 1],
    [1, 0],
  ]),
  'Y': def_gate([
    [0, -1j],
    [1j, 0],
  ]),
  'Z': def_gate([
    [1, 0],
    [0, -1],
  ]),
}
PAULI_GATES = list(PAULI_MATRIX.keys())


def rand_pauli_term(nq:int, coeff_w:float=1.0) -> PauliTerm:
  coeff = (random_float() * 2 - 1) * coeff_w
  string = ''.join(PAULI_GATES[random_int(4)] for _ in range(nq))
  return coeff, string


def rand_pauli_sum(nq:int, n_terms:int=5, coeff_w:float=1.0) -> List[PauliTerm]:
  strings = set()
  ret: List[PauliTerm] = []
  while len(ret) < n_terms:
    pauli_term = rand_pauli_term(nq, coeff_w)
    coeff, string = pauli_term
    if string in strings: continue
    strings.add(string)
    ret.append(pauli_term)
  return ret


def rand_ham(nq:int=2, n_terms:int=5) -> Ham:
  pauli_sum = rand_pauli_sum(nq, n_terms)
  mat, const = paulis2ham(pauli_sum)
  return mat, random_float()


def paulis2ham(paulis:Union[PauliTerm, List[PauliTerm]]) -> Ham:
  if not isinstance(paulis, list): paulis = [paulis]

  hams: List[PauliMat] = []
  const: float = 0.0
  for pauli in paulis:
    coeff, string = pauli
    if string:
      gates = [PAULI_MATRIX[s] for s in string]
      ham = coeff * reduce(lambda x, y: np.kron(x, y), gates)
      hams.append(ham)
    else:
      const = coeff
  return reduce(lambda x, y: x + y, hams), const


if __name__ == '__main__':
  pauli_sum = rand_pauli_sum(nq=2, n_terms=5)
  print(pauli_sum)

  ham, const = paulis2ham(pauli_sum)
  print(ham.shape)
  print(ham)
