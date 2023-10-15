#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/15

# implement the quantum key distribution, based on BB84 protocol

from qlocal import *


def gen_key(alice:Tuple[List[bit], List[bas]], bob:List[bas]) -> List[bit]:
  ''' Alice picks ([b], [x]), Bob chooses [x] '''

  bs, xs = alice
  xs_ = bob
  assert len(bs) == len(xs) == len(xs_), f'length mismatch: len(b)={len(bs)}, len(x)={len(xs)}, len(x_)={len(xs_)}]'

  res: List[bit] = []
  for b, x, x_ in zip(bs, xs, xs_):
    # step 1: Alice prepare and sends photon |b> on basis x
    phi = make_phi(b, x)

    # step 2: Bob choose basis to measure
    basis = make_basis(x_)
    circuit = f'''
      qbit q;
      {phi}
      {basis}
      M(q);
    '''
    r = shot_circuit((circuit, []))

    # step 3: exchange basis and decide outcome
    if x == x_: res.append(r)

  return res


def make_phi(b:bit, x:bas) -> Circuit:
  gates = []
  if x == 1: gates.append('H(q);')
  if b == 1: gates.append('X(q);')
  return '\n'.join(gates)


def make_basis(x:bas) -> Circuit:
  return 'H(q);' if x == 1 else ''


if __name__ == '__main__':
  from xrand import random_bit

  nlen = 72
  bits_str = lambda x: ''.join([str(e) for e in x])

  xs  = [random_bit() for _ in range(nlen)]
  bs  = [random_bit() for _ in range(nlen)]
  xs_ = [random_bit() for _ in range(nlen)]
  key = gen_key((bs, xs), xs_)

  print('bs:',  bits_str(bs))
  print('xs:',  bits_str(xs))
  print('xs_:', bits_str(xs_))
  print('key:', bits_str(key))
  print('key_gen_ratio:', len(key) / nlen)
