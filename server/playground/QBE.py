#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/11

# Quantum Bit Escrow: https://arxiv.org/pdf/quant-ph/0004017.pdf

import sys
import numpy as np
from isq import LocalDevice

# the constant in paper setting
THETA = np.pi / 8


def randbit() -> int:
  ''' generates a random classical bit 0/1'''
  return 0 if np.random.random() < 0.5 else 1


def run_prog(prog:str) -> int:
  ''' run circuit and get measured result: a classical bit info '''
  ld = LocalDevice(shots=1)   # just once
  res = ld.run(prog)
  return int(list(res.keys())[0])

def measure_under_basis_x0(qubit:str) -> int:
  # basis transform: {phi[b,0]} => computional basis
  # note that x0 basis is -θ biased from computional basis, so we plus it back
  return run_prog(f'''
    qbit q;
    {qubit};
    RY({+2*THETA}, q);
    M(q);
  ''')

def measure_under_basis_x1(qubit:str) -> int:
  # basis transform: {phi[b,1]} => computional basis
  # note that x1 basis is +θ biased from computional basis, so we minus it back
  return run_prog(f'''
    qbit q;
    {qubit};
    RY({-2*THETA}, q);
    M(q);
  ''')

def make_phi(b:int, x:int) -> str:
  '''
    def. phi(α) = cos(α)|0> + sin(α)|1> = RY(2α)
    see also: https://en.wikipedia.org/wiki/List_of_quantum_logic_gates#Rotation_operator_gates

    NOTE: the retval is a gate expression, we later insert it into the circuit template
  '''
  if   b == 0 and x == 0: return f'RY({-2*THETA}, q)'
  elif b == 0 and x == 1: return f'RY({+2*THETA}, q)'
  elif b == 1 and x == 0: return f'RY({np.pi-2*THETA}, q)'
  elif b == 1 and x == 1: return f'RY({np.pi+2*THETA}, q)'


def bit_escrow(b:int):
  ''' protocol 1. in the essay '''

  # step 1: Alice wants to deposit b, she pick random x, send Bob a qubit |phi[b,x]>
  x = randbit()
  phi = make_phi(b, x)

  # step 2: randomly announce a challenge
  c = randbit()
  if c == 0:    # Alice reveal, sends b and x to Bob
    # Bob now knows |phi>, b and x, he measures |phi> under basis x, aka. {phi[0,x], phi[1,x]}
    if x == 0: r = measure_under_basis_x0(phi)
    if x == 1: r = measure_under_basis_x1(phi)
    # Verify result is as Alice claims
    assert r == b
    print(f'>> Bob reveals: {r}')
  else:         # Bob return |phi> to Alice
    # The same thing, but Alice knows all and she does the measurement
    if x == 0: r = measure_under_basis_x0(phi)
    if x == 1: r = measure_under_basis_x1(phi)
    # and assures the returned |phi> is just the same as what she sent before
    assert r == b
    print(f'>> Bob returns: {r}')


def qunatum_coin_flipping():
  ''' protocol 2. in the essay '''

  # step 1: Alice picks b and x randomly, send Bob a qubit |phi[b,x]>
  b = randbit()
  x = randbit()
  phi = make_phi(b, x)

  # step 2: Bob chooses a classical bit b', send to Alice
  b_ = randbit()

  # step 3: Alice sends b and x to Bob, now Bob knows eveything and check if Alice cheat
  if x == 0: r = measure_under_basis_x0(phi)
  if x == 1: r = measure_under_basis_x1(phi)
  assert r == b, '<< Alice cheats!!'

  # step 4: both Alice and Bob knows the final decided random bit
  return b ^ b_


if __name__ == '__main__':
  print('[bit_escrow]')
  for _ in range(10):
    # Alice wants to deposit a classical bit b
    b = randbit()
    print(f'>> Alice escrows: {b}')
    bit_escrow(b)

  print()

  print('[qunatum_coin_flipping]')
  ok, tot = 0, 1000
  print(f'>> gen rand bits: ', end='')
  for _ in range(tot):
    r = qunatum_coin_flipping()
    if r == 0: ok += 1
    print(r, end='') ; sys.stdout.flush()
  print()
  print(f'>> P(0) = {ok / tot:%}')
