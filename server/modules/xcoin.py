#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/14

# implement the quantum coin flipping, based on quantum bit escrow protocol

from qlocal import *

# the constant in paper setting
THETA = np.pi / 8


def toss_coin(alice:Tuple[bit, bas], bob:bit) -> bit:
  ''' Alice picks (b, x), Bob chooses b '''

  # step 1: Alice picks b and x randomly, send Bob a qubit |phi[b,x]>
  b, x = alice
  phi = make_phi(b, x)

  # step 2: Bob chooses a classical bit b', send to Alice
  b_ = bob

  # step 3: Alice sends b and x to Bob, now Bob knows eveything and check if Alice cheat
  basis = make_basis(x)
  circuit = f'''
    qbit q;
    {phi}
    {basis}
    M(q);
  '''
  r = shot_circuit((circuit, []))
  assert r == b, '<< Alice cheats!!'

  # step 4: both Alice and Bob knows the final decided random bit
  return b ^ b_


def make_phi(b:bit, x:bas) -> Circuit:
  ''' def. phi(α) = cos(α)|0> + sin(α)|1> = RY(2α) '''
  if   b == 0 and x == 0: tht = -2*THETA
  elif b == 0 and x == 1: tht = +2*THETA
  elif b == 1 and x == 0: tht = np.pi-2*THETA
  elif b == 1 and x == 1: tht = np.pi+2*THETA
  return f'RY({tht}, q);'


def make_basis(x:bas) -> Circuit:
  if   x == 0: tht = +2*THETA
  elif x == 1: tht = -2*THETA
  return f'RY({tht}, q);'


if __name__ == '__main__':
  b, x = randb(), randb()
  print(f'Alice: b = {b}, x = {x}')
  b_ = randb()
  print(f'Bob: b = {b_}')

  r = toss_coin((b, x), b_)
  assert r == b ^ b_
  print(f'Result: r = {r}')
