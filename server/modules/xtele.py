#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/11

# implement the quantum teleportation: sends an arbitary quantum state through pre-distributed EPR-pair and classical communication between

from modules.qcloud import *
from modules.qlocal import *
from modules.qbloch import *


@timer
def teleport(phi:Phi) -> Freq:
  isq = build_circuit(phi)
  res = submit_program(isq, 3000)
  return sum(res[::2]), sum(res[1::2])


def build_circuit(phi:Phi) -> Circuit:
  ''' quantum teleportation circuit: Alice(|0>,|1>) Bob(|2>) '''

  return '''
    import std;
    qbit q[3];
    unit main() {
      H(q[1]);
      CNOT(q[1], q[2]);
      ENCODE_STATE
      CNOT(q[0], q[1]);
      H(q[0]);
      if (M(q[1])) { X(q[2]); }
      if (M(q[0])) { Z(q[2]); }
      M(q[2]);
    }
  '''.replace('ENCODE_STATE', encode_state(phi, 0))


def encode_state(phi, qubit:int=0, impl:str='U3') -> Circuit:
  ''' prepare state: |phi> = a|0> + b|1> '''

  tht, psi = phi2loc(phi)

  if impl == 'U3':
    encoder = f'U3({tht:.5f}, {psi:.5f}, 0, q[{qubit}]);'
  else:
    encoder = f'''
      Ry({tht:.5f}, q[{qubit}]);
      Rz({psi:.5f}, q[{qubit}]);
      GPhase({psi/2:.5f});
    '''
  return encoder


if __name__ == '__main__':
  phi = rand_phi()
  print('phi:', phi)
  prob = phi2prob(phi)
  print('prob:', prob)

  c0, c1 = teleport(phi)
  tot = c0 + c1
  print(f'p0 = {c0 / tot:.3f}, p1 = {c1 / tot:.3f}')
