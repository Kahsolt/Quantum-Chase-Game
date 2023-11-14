#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from modules.xrand import *
from services.shared import *
from services.domains import item


def warm_up():
  ''' pre-heat the random circuits '''

  print('>> prepare general random')
  random_bit()
  random_float()

  print('>> prepare item spawn random')
  weight = list(SPAWN_WEIGHT.values())
  fp = CACHE_PATH / 'item-spawn.json'
  if fp.exists():     # expire cache if weight has changed
    *pack, extras = load_circuit(fp, has_extras=True)
    if extras['w'] != weight:
      fp.unlink()

  if not fp.exists():
    kl = 1
    while kl > 1e-3:
      pack = train_random(weight, steps=5000, lr=0.2)
      kl = verify_random(pack, weight)
      print('  kl:', kl)
    save_circuit(pack, fp, extras={'w': weight, 'kl': kl})

  pack = load_circuit(fp)
  item.spawn_rand = pack

  # show compare
  tprob = freq2prob(list(SPAWN_WEIGHT.values()))
  pprob = run_circuit_probs(pack)
  qprob = freq2prob(sample_circuit(pack, shots=10000))
  keys = list(SPAWN_WEIGHT.keys())

  print('spawn prob: (truth / pmeas / qmeas)')
  for k, pt, pp, pq in zip(keys, tprob, pprob, qprob):
    print(f'{k}: {pt:.3%} / {pp:.3%} / {pq:.3%}')
