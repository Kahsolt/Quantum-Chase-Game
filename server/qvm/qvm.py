#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

# The isQ-open (reduced version) service

from utils import *

qvm = LocalDevice(shots=SHOTS)


class with_shots:
  def __init__(self, shots:int):
    self.shots = shots
    self.shots_saved = qvm._shots
  def __enter__(self):
    qvm._shots = self.shots
  def __exit__(self, exc_type, exc_val, exc_tb):
    qvm._shots = self.shots_saved


def init_params(n_params:int) -> Params:
  return np.random.uniform(low=-1, high=1, size=[n_params]) * (np.pi / 4) / 32


def train_circuit(pack:CircuitPack, loss_fn:Callable[[Params], float], steps:int=1000, lr:float=0.1, eps:float=1e-8, log:bool=True) -> CircuitPack:
  circuit, params = pack
  opt = optimizer(lr=lr)
  for i in range(steps):
    params, loss = opt.opt(loss_fn, params)
    if loss < eps: break
    if log and i % 100 == 0: print(f'[step {i}] loss: {loss}, lr: {opt._lr}')
    if i > 0 and i % 1000 == 0: opt._lr /= 2
  return circuit, params


def run_circuit_state(pack:CircuitPack) -> State:
  ''' Evolution '''

  circuit, params = pack
  kwargs = {VARGS: optv(params)}
  args = qvm.compile_with_par(circuit, **kwargs)

  from isq.simulate.simulator import set_mod, check, getstate, shift
  mod = 0   # use numpy.autograd
  set_mod(mod)
  line_data = qvm._ir.split('\n')
  qnum, qdic = check(line_data)
  state, mq = getstate(line_data, qnum, qdic, mod, **args)
  state = shift(state, qnum, mq)
  return state


def run_circuit_probs(pack:CircuitPack) -> Prob:
  ''' PMeasure '''

  circuit, params = pack
  kwargs = {VARGS: optv(params)}
  return qvm.probs(circuit, **kwargs)


def shot_circuit(pack:CircuitPack) -> str:
  ''' QMeasure once '''

  circuit, params = pack
  with with_shots(1):
    res = qvm.run(circuit, **{VARGS: optv(params)})
  cb: str = list(res.keys())[0]
  return bin2dec(cb)


def sample_circuit(pack:CircuitPack, shots:int=SHOTS) -> Freq:
  ''' QMeasure many '''
  
  assert shots > 0, f'`shots` must be postive, but got {shots}'
  circuit, params = pack
  with with_shots(shots):
    res = qvm.run(circuit, **{VARGS: optv(params)})

  nq = int(REGEX_NQ.findall(circuit)[0][0])   # FIXME: this is not safe :(
  ret = [0] * (2 ** nq)
  for k, v in res.items():
    ret[bin2dec(k)] = v
  return ret


def save_circuit(pack:CircuitPack, fp:Path):
  circuit, params = pack
  data = {
    'isq': [e.strip() for e in circuit.strip().split('\n')],
    'params': params,
  }
  with open(fp, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)
  print(f'>> save to {fp}')


def load_circuit(fp:Path) -> CircuitPack:
  with open(fp, 'r', encoding='utf-8') as fh:
    data = json.load(fh)
  print(f'>> load from {fp}')
  return '\n'.join(data['isq']), data['params']


if __name__ == '__main__':
  isq = '''
    qbit q[2];
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0:2]);
'''
  pack = (isq, [])

  fp = Path(os.environ.get('TMP', '.')) / 'test_circuit.json'
  save_circuit(pack, fp)
  pack = load_circuit(fp)

  res = run_circuit_state(pack)
  print('[run_circuit_state]')
  print('>>', res)

  res = run_circuit_probs(pack)
  print('[run_circuit_probs]')
  print('>>', res)

  print('[shot_circuit]')
  res = shot_circuit(pack)
  print('>> dec:', res)
  print('>> bin:', dec2bin(res))

  res = sample_circuit(pack, shots=100)
  print('[sample_circuit] (shots=100)')
  print('>> freq:', res)
  print('>> prob:', freq2prob(res))