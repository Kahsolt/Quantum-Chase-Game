#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/11

# implement the quantum teleportation: sends an arbitary quantum state through pre-distributed EPR-pair and classical communication between

from qcloud import *
from qlocal import *
from qbloch import *

Phi = Tuple[complex, complex]


def make_teleportation(phi:Phi) -> Circuit:
  ''' quantum teleportation circuit '''

  circuit = '''
qbit q[3];
unit main() {
  // charlie
  H(q[0]);
  CNOT(q[0], q[1]);

  // alice
  ENCODE_STATE
  CNOT(q[2], q[0]);
  H(q[2]);
  int c0 = M(q[0]);
  int c1 = M(q[2]);

  // bob
  if (c2 == 1) { Z(q[1]); }
  if (c0 == 1) { X(q[1]); }
  M(q[1]);
}
'''.replace('ENCODE_STATE', encode_state(phi, 2))

  if not 'debug':
    print(circuit)

  return circuit


def encode_state(phi, qubit:int=0) -> Circuit:
  ''' prepare state: |phi> = a|0> + b|1> '''
  tht, psi = phi2loc(phi)
  return f'U3({tht}, {psi}, 0, q[{qubit}]);'


def rand_phi() -> Phi:
  tht = rand() * pi
  psi = rand() * 2 * pi
  phi = loc2phi((tht, psi))
  phi /= phi[0]
  phi /= abs(phi)
  return phi.tolist()


def test_encode_state(cnt:int=10):
  circuit = '''
    qbit q[1];
    ENCODE_STATE
    M(q[0]);
  }'''

  for _ in range(cnt):
    phi = rand_phi()
    print('phi:', phi)
    cir = circuit.replace('ENCODE_STATE', encode_state(phi))
    print(cir)
    res = run_circuit_state((cir, None))
    print(res)


if __name__ == '__main__':
  test_encode_state(10)
  print()

  phi = rand_phi()
  print('phi:', phi)

  isq = make_teleportation(phi)
  print('prog:')
  print(isq)

  res = submit_program(isq)
  print(res)
