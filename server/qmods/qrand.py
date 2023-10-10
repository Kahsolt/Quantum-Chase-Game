#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

# train an arbitrary distribution random generator with vqc

from utils import *


def make_random(weight:Weight, retry:int=5) -> CircuitPack:
  while retry > 0:
    pack = train_random(weight)
    score = verify_random(pack, weight)
    if score <= 0.1: break
    retry -= 1
  if score > 0.1:
    raise Exception(f'cannot make random on weights: {weight}')
  return pack


def build_circuit(nq:int) -> Tuple[Circuit, int]:
  ''' strong-entangle ansatz (with random drop) '''

  QREG = f'qbit q[{nq}];'
  QMES = f'M(q[0:{nq}]);'
  QCIR = []

  n_params = 0
  for repeat in range(nq):
    # rot
    for i in range(nq):
      if rand() < 0.75:
        QCIR.append(f'RX({VARGS}[{n_params}], q[{i}]);')
        n_params += 1
      if rand() < 0.75:
        QCIR.append(f'RY({VARGS}[{n_params}], q[{i}]);')
        n_params += 1

    # entgl
    if repeat == nq - 1: continue
    for i in range(nq - 1):   # linear
      if rand() < 0.75:
        QCIR.append(f'CNOT(q[{i}], q[{i+1}]);')
    for i in range(nq):       # rand
      if rand() < 0.75:
        x, y = randn(nq), randn(nq)
        if x == y: continue
        QCIR.append(f'CNOT(q[{x}], q[{y}]);')

  circuit = '\n'.join([QREG] + QCIR + [QMES])
  n_params += 1

  if not 'debug':
    print('n_params:', n_params)
    print(circuit)

  return circuit, n_params

@timer
def train_random(weight:Weight, steps:int=5000, lr:float=0.07) -> CircuitPack:
  target = weight2prob(weight)
  nq = int(math.log2(len(target)))

  circuit, n_params = build_circuit(nq)
  params = np.random.uniform(low=-np.pi/4, high=np.pi/4, size=[n_params])

  def loss_fn(params:Params) -> float:
    probs = run_circuit((circuit, params))
    return ((probs - target)**2).sum()   # mseloss

  opt = optimizer(lr=lr)
  for i in range(steps):
    params, loss = opt.opt(loss_fn, params)
    if loss < eps: break
    if i % 100 == 0: print(f'[step {i}] loss: {loss}')
    if i % 1000 == 0: opt._lr /= 2

  return circuit, params


def verify_random(pack:CircuitPack, weight:Weight, shots:int=10000) -> float:
  ''' KL-div for distribution, the smaller the better '''

  target = weight2prob(weight)
  freq = sample_circuit(pack, shots, fmt='frq')
  return kl_div(np.asarray(freq), np.asarray(target))


if __name__ == '__main__':
  weight = [1, 2, 3]
  pack = train_random(weight)
  sc = verify_random(pack, weight, shots=30000)
  print('kl_div score:', sc)

  res = sample_circuit(pack, shots=1000)
  print(res)
  res = sample_circuit(pack, shots=3000, fmt='frq')
  print(res)
