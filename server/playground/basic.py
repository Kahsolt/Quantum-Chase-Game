#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq import LocalDevice


def run_prog(prog:str):
  ld = LocalDevice(shots=1000)
  res = ld.run(prog)
  print(res)


# fair coin
run_prog('''
  qbit a;
  H(a);
  M(a);
''')

# unfair coin
run_prog('''
  qbit a;
  RX(0.75, a);
  M(a);
''')

# EPR state
run_prog('''
  qbit a, b;
  H(a);
  CNOT(a, b);
  M(a);
  M(b);
''')

# GHZ state
run_prog('''
  qbit qv[3];
  H(qv[0]);
  CNOT(qv[0], qv[1]);
  CNOT(qv[1], qv[2]);
  M(qv[0:3]);
''')
