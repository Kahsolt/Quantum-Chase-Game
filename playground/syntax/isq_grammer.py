#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

# qubit

'''
qbit q;         // qbit
qbit qv[3];     // qreg
qbit q, p[5];
'''

# user-def oracle gate
# matlab-like, must be on top of the program

'''
defgate Rs = [
  0.5+0.8660254j,0,0,0;
  0,1,0,0;
  0,0,1,0;
  0,0,0,1
]
'''

# gate

'''
H(q);
H(p[1+2]);
CNOT(q, p[1]);
CNOT(p[1:3], p[2:4]);   // = CNOT(p[1], p[2]), CNOT(p[2], p[3])
Z(p[1,3]);              // = Z(p[1]), Z(p[3]);
RX(0.5, q);

[basic gates]
  H, X, Y, Z, S, T
  SD, TD, X2P, X2M, Y2P, Y2M
  CX, CY, CZ, CNOT
  RX, RY, RZ, RXY

=> only C-X is double-qubit gate
'''

# measure

'''
M(q);
M(p[1]);
M(p[1:4]);    // = M(p[1]), M(p[2]), M(p[3]);

'''

# if

'''
if (expression asso expression) {
  ifBody
}

if (expression asso expression ) {
  ifBody
} else {
  elseBody
}

=> expression is int const or expr
=> valid asso: >,>=,<,<=,==,!=
'''

# for

'''
for i in start:stop:step {
  forloopBody
}

for i in 1:3 {
  H(t[i]);
  CZ(w[i],w[i+1]);
}
'''
