#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/12

# C-like grammer: https://www.arclightquantum.com/isq-docs/latest/grammar/

# package

'''
// java-like package decleration
package aaa;
int g;
'''

# import

'''
package ddd;
import aaa.ccc;   // ./aaa/ccc.isq
import std;       // ${ISQ_ROOT}/lib/std.isq
'''

# main entry

'''
unit main(int i_par[], double d_par[]) {
  ...
  Rx(d_par[0], q);
  if (i_par[1] == 2) {...}
  ...
}
'''

# types

'''
  int: a 64-bit signed integer, e.g. -1, 1;
  bool: a boolean value that can be either true or false;
  double: a double precision floating point number, e.g. -0.1, 3.1415926;
  unit: the return type of a procedure that returns nothing;
  qbit: an opaque type that represents a quantum bit;
'''

'''
// global variable
int a, b = 4; // int variables
double d = pi; // double variable with initial value 3.14159...
qbit q; // qbit

procedure main() {    
  // local variable with initial value 3 
  int c = 3;
  ...
}
'''

# array

'''
qbit q[3]; // the length of a global array must be a positive integer

unit main() {
  // when an array is initilized, the length should not be specified
  int a[] = [1, 2]; 

  // a local variable may use expressions as length
  int b[a.length];
  ...
}
'''

# classical operation

'''
  Arithmetic operators: +, -, *, /, ** (power), %
  Comparison operators: ==, !=, >, <, >=, <=
  Logical operators: &&, and, ||, or, !, not
  Bitwise operators: &, |, ^(XOR)
  Shift operators: >>, <<
'''

'''
unit main() {
  int a = 2 * (3 + 4) % 3;
  double d = 3.14 * a;

  print a;
  print d;
}
unit main() {
  assert true;    // OK
  assert(3 == 4); // Causing a program abort
}
'''

# quantum operation

'''
basic gates: X, Y, Z, H, S, T, Rx, Ry, Rz, CNOT, Toffoli, U3
non-unitary operation: M(measure), |0> (set qubit to |0>)
'''

# procedure

'''
// proceduer with two qbit as paramters and has no return
// paramtesr can also be written like (a: qbit, b: qbit)
unit swap(qbit a, qbit b) {
  ...
}

// proceduer with two classical paramters and return with a double
double compute(int a, double b[]) {
  double s = 0.0;
  ...
  return s;
}

// entry procedure
unit main() {
  qbit q[2];
  // call swap
  swap(q[0], q[1]);

  double b[2];
  // call compute
  double c = compute(1, b);
}
'''

# oracle

'''
// g(n, m): n working qubits, m ancilla qubits
oracle g(2, 1) = [0, 1, 0, 0];

qbit q[3];

unit main() {
  ...
  g(q[2], q[1], q[0]);
  ...
}
'''

'''
oracle bool[1] g(bool x[2]) {
  bool res[] = {x[0] && !x[1]};
  return res; 
}
unit main() {
  qbit p[2], q[1];
  ...
  g(p, q);
  ...
}
'''

# qubit

'''
qbit q;         // qbit
qbit qv[3];     // qreg
qbit q, p[5];
'''

# measure

'''
M(q);
M(p[1]);
M(p[1:4]);    // = M(p[1]), M(p[2]), M(p[3]);
'''

# user-def oracle gate: # matlab-like, must be on top of the program

'''
defgate Rs = [
  0.5+0.8660254j,0,0,0;
  0,1,0,0;
  0,0,1,0;
  0,0,0,1
]
'''

# deriving gate through a q-procedure

'''
// pure quantum procedure that swap two qbit
unit swap(qbit a, qbit b) {
  CNOT(b, a);
  CNOT(a, b);
  CNOT(b, a);
} deriving gate

unit main() {
  qbit q[3];
  // set |q> -> |110>
  X(q[0]);
  X(q[1]);
  // controlled-swap, set |q> -> |101> 
  ctrl swap(q[0], q[1], q[2])
}
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

# modifiers

'''
  ctrl: modify gate to controlled-gate, can has a paramter representing the number of control qubits(defualt is 1).
  nctrl: modify gate to neg-controlled-gate, can has a paramter representing the number of control qubits(defualt is 1).
  inv: modify gate to conjugate transpose.
'''

'''
unit main() {
  qbit p, q, r;

  // p ---●---
  //      |  
  // q ---S---
  ctrl S(p, q);

  // p ---●---
  //      |  
  // q ---●---
  //      |  
  // r ---S---
  ctrl<2> S(p, q, r);

  // q ---S^{-1}---
  inv S(q);

  // p --X--●--X---
  //        |  
  // q ---S^{-1}---
  nctrl inv S(p, q);
}
'''

'''
When a group of gates share the same control qubits, sometimes it is better to use a switch-case statement. For example

  qbit q[2], p, r;
  switch q {
  case |3>:
    ctrl Rx(pi, r, p);
  default:
    H(p);
  }

It is equivalent to the following statements

  nctrl nctrl H(q[1], q[0], p);
  nctrl ctrl H(q[1], q[0], p);
  ctrl nctrl H(q[1], q[0], p);
  ctrl ctrl Rx(pi, q[1], q[0], p);
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
  CZ(w[i], w[i+1]);
}

int a[] = {2, 3, 4};
for v in a {
  print v;
}
'''

# while

'''
unit main() {
  bool a = true;
  qbit q;
  while (!a) {
    H(q);
    a = M(q);
  }
}
'''

# switch-case

'''
unit main() {
  int a = 1, b;
  switch a {
    case 1:
      b = 3;
    case 2:
      b = 4;
    default:
      b = 5;
  }
}
'''
