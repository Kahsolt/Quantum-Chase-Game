#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

# train an arbitrary distribution random generator with vqc

import math
from functools import partial

from modules.qlocal import *

Weight = List[Union[float, int]]
kl_div = lambda x, y: np.mean(x * (np.log(x + 1e-15) - np.log(y + 1e-15)))

# n-faces dice (cached)
dices: Dict[int, CircuitPack] = {}


def random_bit() -> bit:
  return random_int(2)


def random_int(n:int) -> int:
  pack = _prepare_dice(n)
  r = n + 1
  while r > n:
    r = shot_circuit(pack)
  return r


def random_float() -> float:
  bits = [random_bit() for _ in range(32)]
  val, unit = 0.0, 1
  for b in bits:
    unit /= 2
    val += b * unit
  return val


def _prepare_dice(n:int) -> CircuitPack:
  assert n >= 2, 'n should >=2'
  if n in dices: return dices[n]

  print('>> _prepare_dice:', n)
  cache_fp = CACHE_PATH / f'dice-{n}.json'
  if not cache_fp.exists():
    if n & (n - 1) == 0:    # power of 2, use H only
      nq = int(np.log2(n))
      circuit = '\n'.join([
        f'qbit q[{nq}];'
        *[f'H({i});' for i in range(nq)],
        f'M(q[0:{nq}]);'
      ])
      pack = circuit, []
    else:
      w = np.ones(n) / n    # uniform
      pack = make_random(w, retry=10, thresh=0.05)
    save_circuit(pack, cache_fp)
  dices[n] = load_circuit(cache_fp)
  return dices[n]


def make_random(weight:Weight, retry:int=5, thresh:float=0.1) -> CircuitPack:
  while retry > 0:
    pack = train_random(weight)
    score = verify_random(pack, weight)
    if score <= thresh: break
    retry -= 1
  if score > thresh:
    raise Exception(f'cannot make random on weights: {weight}')
  return pack


def build_circuit(nq:int) -> Tuple[Circuit, int]:
  ''' strong-entangle ansatz (with random drop) '''

  QREG = f'qbit q[{nq}];'
  QMES = f'M(q[0:{nq}]);'
  QCIR = []

  rand  = lambda  : np.random.random ()     # classical random float
  randn = lambda n: np.random.randint(n)    # classical random int

  n_params = 0
  for repeat in range(nq):
    # rot
    for i in range(nq):
      if rand() < 0.5:
        QCIR.append(f'RX({VARGS}[{n_params}], q[{i}]);')
        n_params += 1
      if rand() < 0.75:
        QCIR.append(f'RY({VARGS}[{n_params}], q[{i}]);')
        n_params += 1

    # entgl
    if repeat == nq - 1: continue
    for i in range(nq - 1):   # linear
    #  if rand() < 0.75:
        QCIR.append(f'CNOT(q[{i}], q[{i+1}]);')
    #for i in range(nq):       # rand
    #  if rand() < 0.75:
    #    x, y = randn(nq), randn(nq)
    #    if x == y: continue
    #    QCIR.append(f'CNOT(q[{x}], q[{y}]);')

  circuit = '\n'.join([QREG] + QCIR + [QMES])

  if not 'debug':
    print('n_params:', n_params)
    print(circuit)

  return circuit, n_params


@timer
def train_random(weight:Weight, steps:int=5000, lr:float=0.1) -> CircuitPack:
  target = _weight2prob(weight)
  nq = int(math.log2(len(target)))

  circuit, np = build_circuit(nq)
  params = init_params(np)
  pack = circuit, params

  def loss_fn(target:Prob, circuit:Circuit, params:Params) -> float:
    probs = run_circuit_probs((circuit, params))
    return ((probs - target)**2).sum()   # mseloss

  return train_circuit(pack, partial(loss_fn, target, circuit), steps, lr)


def verify_random(pack:CircuitPack, weight:Weight, shots:int=10000) -> float:
  ''' KL-div for distribution, the smaller the better '''

  target = _weight2prob(weight)
  freq = freq2prob(sample_circuit(pack, shots))
  return kl_div(np.asarray(freq), np.asarray(target))


def _weight2prob(weight:Weight) -> Prob:
  w = np.asarray(weight)
  prob = w / w.sum()
  nc = len(prob) ; assert nc >= 2, 'prob dist length must >= 2'
  nq = math.ceil(math.log2(nc))
  return np.pad(np.asarray(prob), (0, 2 ** nq - nc)).tolist()


if __name__ == '__main__':
  weight = [1, 2, 3]
  pack = train_random(weight)
  sc = verify_random(pack, weight, shots=30000)
  print('kl_div score:', sc)

  for _ in range(10):
    res = shot_circuit(pack)
    print(res)

  res = sample_circuit(pack, shots=1000)
  print(res)
  res = sample_circuit(pack, shots=3000)
  print(res)
