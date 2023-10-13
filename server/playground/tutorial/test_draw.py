#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import LocalDevice
import matplotlib.pyplot as plt

isq_str = '''
  qbit a,b;
  H(a);
  CNOT(a,b);
  RX(2.333, a);
  M(a);
  M(b);
'''

ld = LocalDevice()
ld.run(isq_str)

ld.draw_circuit()
plt.show()
ld.draw_circuit(showparam=True)
plt.show()
