#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/11

# implement the quantum teleportation: sends an arbitary quantum state through pre-distributed EPR-pair and classical communication between

from utils import *

Phi = Tuple[complex, complex]
rand_pi = lambda: (rand() * 2 - 1) * pi


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
  if (c2 == 0) {
    if (c0 == 0) {
      ;
    } else {
      X(q[1]);
    }
  } else {
    if (c0 == 0) {
      Z(q[1]);
    } else {
      Z(q[1]);
      X(q[1]);
    }
  }
  M(q[1]);
}
'''.replace('ENCODE_STATE', encode_state(*phi, 2))

  if not 'debug':
    print(circuit)

  return circuit


def encode_state(a:complex, b:complex, qubit:int=0) -> Circuit:
  ''' prepare state: |phi> = a|0> + b|1> '''
  
  tht = 2 * np.arccos(a)
  phi = np.log(b / np.sin(tht / 2) + 1e-15) / 1j
  lbd = 0
  breakpoint()
  return f'U3({tht}, {phi}, {lbd}, q[{qubit}]);'


def rand_phi() -> Phi:
  a, b, c, d = rand_pi(), rand_pi(), rand_pi(), rand_pi()
  phi = np.asarray([complex(a, b), complex(c, d)], dtype=np.complex128)
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
    cir = circuit.replace('ENCODE_STATE', encode_state(*phi))
    print(cir)
    res = run_circuit_state((cir, None))
    print(res)


if __name__ == '__main__':
  test_encode_state(10)
  print()

  phi = rand_phi()
  print('phi:', phi)

  circuit = make_teleportation(phi)
  print('circuit:')
  print(circuit)
  pack = (circuit, None)

  res = run_circuit_state(pack)
  print(res)
  res = run_circuit_probs(pack)
  print(res)
  res = sample_circuit(pack, 1000)
  print(res)
