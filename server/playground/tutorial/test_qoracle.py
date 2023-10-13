#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import qpu
from isq import quantumCor, LocalDevice

Rs = [
  [0.5+0.8660254j,0,0,0],
  [0,1,0,0],
  [0,0,0,1],
  [0,0,1,0]
]

quantumCor.addGate('Rs', Rs)

ld = LocalDevice()
@qpu(ld)
def test():
  '''
    qbit a, b;
    H(a);
    Rs(a, b);
    M(a);
  '''

res = test()
print(res)
