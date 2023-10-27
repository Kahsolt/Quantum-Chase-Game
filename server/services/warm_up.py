#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/27

from modules.xrand import *
from services.models import SPAWN_WEIGHT
from services.domains import item


def warm_up():
  ''' pre-heat the random circuits '''

  print('>> prepare general random')
  random_bit()
  random_float()

  print('>> prepare item spawn random')
  fp = CACHE_PATH / 'item-spawn.json'
  if not fp.exists():
    weight = list(SPAWN_WEIGHT.values())
    pack = train_random(weight)
    save_circuit(pack, fp)
    kl = verify_random(pack, weight)
    print('  kl:', kl)

  pack = load_circuit(fp)
  item.spawn_rand = pack
  res = sample_circuit(pack, shots=3000)
  print('  pdist:', freq2prob(res))
