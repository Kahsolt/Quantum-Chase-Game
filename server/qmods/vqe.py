#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

# VQE: train a vqc to approx minimal eigen of given ham matrix

from utils import *

Ham = ndarray
EigenVal = float
EigenVec = ndarray
Eigen = Tuple[EigenVal, EigenVec]

eps = 1e-5


def gen_ham(nq:int=2) -> Ham:
  dim = 2 ** nq
  h = np.random.uniform(size=[dim, dim])
  h = (h + h.conj().T) / 2
  return h


def exp_ham(ham:Ham, vec:State) -> float:
  # calc Rayleigh quotient: <x|H|x>
  return np.abs(vec @ ham @ vec)


def npy_solver(ham:Ham) -> Eigen:
  vals, vecs = np.linalg.eigh(ham)
  idx = vals.argmin()
  return vals[idx], vecs[:, idx]


@timer
def vqe_solver(circuit:Circuit, ham:Ham) -> Eigen:
  np = len(REGEX_V.findall(circuit))
  params = init_params(np)
  pack = circuit, params

  def loss_fn(circuit:Circuit, params:Params) -> float:
    state = run_circuit_state((circuit, params))
    return exp_ham(ham, state)    # ham expectation

  pack = train_circuit(pack, partial(loss_fn, circuit), steps=5000, lr=0.1)
  state = run_circuit_state(pack)
  breakpoint()
  gs_ene = exp_ham(ham, state)
  return gs_ene, state


def calc_error(val:float, ref:float) -> Tuple[float, float]:
  ''' Absolute error & relative error rate '''

  err = abs(val - ref)
  err_r = err / abs(ref)
  return err, err_r


if __name__ == '__main__':
  circuit = f'''
    qbit q[2];
    RY({VARGS}[0], q[0]);
    RY({VARGS}[1], q[1]);
    CNOT(q[0], q[1]);
    RY({VARGS}[2], q[0]);
    RY({VARGS}[3], q[1]);
    CNOT(q[0], q[1]);
    RY({VARGS}[4], q[0]);
    RY({VARGS}[5], q[1]);
    M(q[0:2]);
'''

  ham = gen_ham()
  print(ham)

  ref, vec = npy_solver(ham)
  print('ref:', ref, 'vec:', vec)
  val, vec = vqe_solver(circuit, ham)
  print('val:', val, 'vec:', vec)

  err, err_r = calc_error(val, ref)
  print(f'error: {err}')
  print(f'error rate: {err:.5%}')
