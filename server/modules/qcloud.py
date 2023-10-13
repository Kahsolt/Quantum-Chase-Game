#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

# The isQ (full version) service (running on cloud, e.g. docker)

import requests as R
from requests import Response

from qlocal import Freq
from utils import SHOTS, timer

API_BASE = 'http://127.0.0.1:5001'


def POST(api:str, payload:object) -> Freq:
  resp: Response = R.post(f'{API_BASE}{api}', json=payload, timeout=5)
  if not resp.ok:
    raise RuntimeError(f'HTTP error: {resp.status_code} {resp.reason}')
  return resp.json()


def submit_program(prog:str, shots:int=SHOTS) -> Freq:
  payload = {
    'isq': prog,
    'shots': shots
  }
  r =  POST('/run', payload)
  if not r['ok']:
    raise RuntimeError(r['error'])
  return r['data']


if __name__ == '__main__':
  isq = '''
    import std;
    qbit q[2];
    unit bell_state() {
      H(q[0]);
      CNOT(q[0], q[1]);
    }
    unit main() {
      bell_state();
      int a = M(q[0]);
      int b = M(q[1]);
      print a + b;
    }
  '''

  @timer
  def run(shot:int):
    res = submit_program(isq, shot)
    print(res)

  for shot in [100, 500, 1000, 5000, 10000, 30000]:
    run(shot)
