#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/11

from qvm import *

# gate, param, qubits
# e.g.:
#   (H, None, 1)        => H(q[1])
#   (RX, 'pi/2', 0)     => RX(pi/2, q[0])
#   (RZ, 0.1, 0)        => RZ(0.1, q[0])
#   (RY, 4, 0)          => RY({VARGS}[4], q[0])
#   (CNOT, None, (0,1)) => CNOT(q[0], q[1])
Operation = Tuple[str, Optional[Union[str, float, int]], Union[int, Tuple[int]]]


def convert_circuit(operations:List[Operation], nq:int) -> Tuple[Circuit, int]:
  ''' convert GUI circuit to isq format '''

  QREG = f'qbit q[{nq}];'
  QMES = f'M(q[0:{nq}]);'
  QCIR = []

  n_params = 0
  for op in operations:
    gate, param, qubits = op

    if param is None:
      param_str = ''
    else:
      if isinstance(param, str):
        param_str = param
      elif isinstance(param, float):
        param_str = str(param)
      elif isinstance(param, int):    # vqc
        param_str = f'{VARGS}[{param}]'
        n_params += 1
      else:
        raise ValueError(f'unknown type {type(param)} for `param` {param}')

    if isinstance(qubits, int):
      qubits_str = f'q[{qubits}]'
    elif isinstance(qubits, tuple):
      qubits_str = ', '.join([f'q[{qb}]' for qb in qubits])
    else:
      raise ValueError(f'unknown type {type(qubits)} for `qubits` {qubits}')

    if param_str:
      QCIR.append(f'{gate}({param_str}, {qubits_str});')
    else:
      QCIR.append(f'{gate}({qubits_str});')

  circuit = '\n'.join([QREG] + QCIR + [QMES])

  if not 'debug':
    print('n_params:', n_params)
    print(circuit)

  return circuit, n_params


if __name__ == '__main__':
  operations = [
    ('RX', 'pi/2', 0),
    ('RY', '-pi/3', 0),
    ('H', None, 0),
    ('T', None, 0),
    ('X', None, 1),
    ('CNOT', None, (0,1)),
    ('RX', 0, 1),
    ('RZ', 1, 0),
    ('RZ', 0.0, 1),
    ('RY', -0.15, 1),
  ]
  circuit, n_params = convert_circuit(operations, 2)
  print('n_params:', n_params)
  print(circuit)
  print()

  theta = np.random.uniform(size=[n_params])
  pack = (circuit, theta)

  res = run_circuit_probs(pack)
  print(res)
  res = sample_circuit(pack, 1000)
  print(res)
