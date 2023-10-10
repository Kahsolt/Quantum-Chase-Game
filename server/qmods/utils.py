#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/10

import math
from time import time
from re import compile as Regex
from typing import *

import numpy as np
from numpy import ndarray
from isq import LocalDevice, optv, optimizer

number = Union[float, int]
Weight = List[number]
Prob = List[float]
Freq = List[number]
Ham = ndarray

Circuit = str
Params = List[float]
CircuitPack = Tuple[Circuit, Params]

bin2dec = lambda x: int(x, base=2)
dec2bin = lambda x: bin(x)[2:]
rand  = lambda:   np.random.random()    # random float
randn = lambda n: np.random.randint(n)  # random int
randb = lambda:             randn(2)    # random bit

eps = 1e-8
kl_div = lambda x, y: np.mean(x * (np.log(x + eps) - np.log(y + eps)))
freq2prob = lambda x: {k: v / sum(x.values()) for k, v in x.items()}
def weight2prob(weight:Weight) -> Prob:
  w = np.asarray(weight)
  prob = w / w.sum()
  nc = len(prob) ; assert nc >= 2, 'prob dist length must >= 2'
  nq = math.ceil(math.log2(nc))
  return np.pad(np.asarray(prob), (0, 2 ** nq - nc)).tolist()

qvm = LocalDevice(shots=1000)
REGEX_NQ = Regex('qbit q\[(\d+)\];')
VARGS = 'theta'

class with_shots:
  def __init__(self, shots:int):
    self.shots = shots
    self.shots_saved = qvm._shots
  def __enter__(self):
    qvm._shots = self.shots
  def __exit__(self, exc_type, exc_val, exc_tb):
    qvm._shots = self.shots_saved


def run_circuit(pack:CircuitPack) -> Prob:
  ''' PMeasure '''

  circuit, params = pack
  probs = qvm.probs(circuit, **{VARGS: optv(params)})
  return probs


def shot_circuit(pack:CircuitPack, base:int=2) -> Union[str, int]:
  ''' QMeasure once '''

  assert base in [2, 10], '`base` must be 2 or 10'
  circuit, params = pack
  with with_shots(1):
    res = qvm.run(circuit, **{VARGS: optv(params)})
  cb = list(res.keys())[0]
  if base == 2: return cb
  else: return bin2dec(cb)


def sample_circuit(pack:CircuitPack, shots:int, fmt:str='cnt') -> Freq:
  ''' QMeasure many '''
  
  assert shots > 0, '`shots` must be postive'
  assert fmt in ['cnt', 'frq'], '`fmt` must be "cnt" or "frq"'
  circuit, params = pack
  with with_shots(shots):
    res = qvm.run(circuit, **{VARGS: optv(params)})

  nq = int(REGEX_NQ.findall(circuit)[0][0])
  nc = 2 ** nq
  if fmt == 'cnt':
    ret = [0] * nc
  else:
    res = freq2prob(res)
    ret = [0.0] * nc
  for k, v in res.items():
    ret[bin2dec(k)] = v
  return ret


def timer(fn):
  def wrapper(*args, **kwargs):
    start = time()
    r = fn(*args, **kwargs)
    end = time()
    print(f'[Timer]: {fn.__name__} took {end - start:.3f}s')
    return r
  return wrapper
