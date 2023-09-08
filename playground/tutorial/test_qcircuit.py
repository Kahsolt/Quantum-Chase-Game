#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import qpu
from isq import LocalDevice

isq_str = '''
  qbit a, b;
  RX(theta[0], a);
  RY(theta[1], b);
  M(a);
  M(b);
'''

ld = LocalDevice(shots=200)
res = ld.run(isq_str, theta=[0.2, 0.4])
print(res)


@qpu(ld)
def test(theta, a):
  '''
    qbit t[5];
    if (a < 5) {
        X(t[0]);
    } else {
        RX(theta[1], t[1]);
    }
    M(t[1]);
  '''

res = test([0.1, 0.2], 7)
print(res)
