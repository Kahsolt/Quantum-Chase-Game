#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

# VQE: train a vqc to approx minimal eigen of given ham matrix

from functools import partial

from qcloud import *
from qlocal import *
from qpauli import *

EigenVal = float
EigenVec = ndarray
Eigen = Tuple[EigenVal, EigenVec]


def npy_solver(ham:Ham) -> Eigen:
  mat, const = ham
  vals, vecs = np.linalg.eigh(mat)
  print(vals)
  idx = vals.argmin()
  return vals[idx] + const, vecs[:, idx]


@timer
def vqe_solver(circuit:Circuit, ham:Ham, optim:str='COBYLA') -> Eigen:
  mat, const = ham
  params = init_params(len(REGEX_V.findall(circuit)))
  pack = circuit, params

  def loss_fn(circuit:Circuit, params:Params) -> float:
    state = run_circuit_state((circuit, params))
    exp = exp_ham(mat, state)    # ham expectation
    #print(f'>> {exp}')
    return exp

  if not 'use isq':
    pack = train_circuit(pack, partial(loss_fn, circuit), steps=5000, lr=0.1)
  else:
    from scipy.optimize import minimize
    res = minimize(partial(loss_fn, circuit), params, method=optim, options={'maxiter':300})
    pack = circuit, res.x

  state = run_circuit_state(pack)
  gs_ene = exp_ham(mat, state) + const
  return gs_ene, state


def exp_ham(h:HamMat, v:State) -> float:
  # calc Rayleigh quotient: <x|H|x>
  return np.real(v @ h @ v)


def calc_error(val:float, ref:float) -> Tuple[float, float]:
  ''' Absolute error & relative error rate '''
  err = abs(val - ref)
  err_r = err / abs(ref)
  return err, err_r


# unittest ↓↓↓

def test_solve_H2():
  # H2 pauli: https://www.arclightquantum.com/isq-docs/latest/examples/vqe/
  pauli_H2 = [
    (-0.4804, ''),
    (+0.3435, 'ZI'), 
    (-0.4347, 'IZ'), 
    (+0.5716, 'ZZ'), 
    (+0.0910, 'YY'), 
    (+0.0910, 'XX'),
  ]
  ham = paulis2ham(pauli_H2)

  circuit = f'''
    qbit q[2];
    X(q[1]);
    RY(pi/2, q[0]);
    RX(3*pi/2, q[1]);
    CNOT(q[0], q[1]);
    RZ({VARGS}[0], q[1]);
    CNOT(q[0], q[1]);
    RY(3*pi/2, q[0]);
    RX(pi/2, q[1]);
  '''

  _run_ham_circuit(ham, circuit)


def test_solve_rand(nq:int=2):
  # strong-entangle ansatz
  # for CHC see: https://pubs.rsc.org/en/content/articlehtml/2020/sc/d0sc01908a
  def build_circuit(nq:int, repeat:int=2) -> Circuit:
    QREG = f'qbit q[{nq}];'
    QENC = 'X(q[1]);'
    QMES = f'M(q[0:{nq}]);'
    QCIR = []

    n_params = 0
    for r in range(repeat):
      # rot
      for i in range(nq):
        QCIR.append(f'RX({VARGS}[{n_params}], q[{i}]);') ; n_params += 1
        QCIR.append(f'RZ({VARGS}[{n_params}], q[{i}]);') ; n_params += 1
      # entgl
      if r == nq - 1: continue
      for i in range(nq - 1):   # linear
        QCIR.append(f'CNOT(q[{i}], q[{i+1}]);')
    
    return '\n'.join([QREG] + [QENC] + QCIR + [QMES])

  ham = rand_ham(nq)
  circuit = build_circuit(nq, repeat=4)
  _run_ham_circuit(ham, circuit)


def _run_ham_circuit(ham:Ham, circuit:Circuit):
  print(circuit)
  print('ham mat:', ham[0])
  print('ham const:', ham[1])
  print()

  ref, vec = npy_solver(ham)
  print('ref:', ref, 'vec:', vec.real.tolist())
  print()
  val, vec = vqe_solver(circuit, ham)
  print('val:', val, 'vec:', vec.real.tolist())
  print()

  err, err_r = calc_error(val, ref)
  print(f'error: {err}')
  print(f'error rate: {err_r:.7%}')
  print('=' * 72)


if __name__ == '__main__':
  #test_solve_H2()
  test_solve_rand()
