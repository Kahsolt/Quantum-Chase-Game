#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/09

import isq
from isq import LocalDevice, optv
import numpy as np

prog = '''
  qbit q[2];
  RX(theta[0], q[0]);
  RY(theta[1], q[1]);
  CNOT(q[0], q[1]);
  RX(theta[2], q[0]);
  RY(theta[3], q[1]);
  M(q[0:2]);
'''

INIT = np.random.uniform(low=-np.pi/4, high=np.pi/4, size=[4])
TGT = np.asarray([1/3, 1/3, 1/3, 0])

ld = LocalDevice(shots=1000)

def loss(params):
  probs = ld.probs(prog, theta=optv(params))
  return ((probs - TGT)**2).sum()   # mseloss

opt = isq.optimizer(0.1)
newp = INIT
for i in range(2000):
  newp, cost = opt.opt(loss, newp)
  if i % 100 == 0: print(f'[step {i}] cost: {cost}')

print('>> final params:', newp)

res = ld.run(prog, theta=optv(newp))
print(res)
