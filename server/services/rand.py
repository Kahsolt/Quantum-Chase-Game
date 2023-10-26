#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/26

from modules.xrand import *
from services.utils import number

# ref: https://www.bilibili.com/read/cv15865943/
# convert: U[0, 1] => N(0, 1)
def random_gaussian() -> float:
  u1 = random_float()
  u2 = random_float()
  f = np.sin if random_bit() else np.cos
  return f(2 * pi * u1) * np.sqrt(-2 * np.log(u2 + 1e-15))


def random_gaussian_expect(val:number, vmin:number=None, vmax:number=None) -> number:
  ''' (|N(0, 1)| + val).clip(vmin, vmax) '''

  v = abs(random_gaussian() + val)
  if vmin is not None: v = max(v, vmin)
  if vmax is not None: v = min(v, vmax)
  return type(val)(v)


def random_uniform_expect(vmin:number=0.0, vmax:number=1.0) -> number:
  ''' U(vmin, vmac) '''

  v = random_float() * (vmax - vmin) + vmin
  return type(vmin)(v)


def random_choice(array:List[Any], weights:List[number]=None) -> Any:
  if weights is None:
    return array[random_int(len(array) - 1)]
  else:
    raise NotImplementedError


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  from tqdm import tqdm

  x = [random_gaussian() for _ in tqdm(range(300))]
  plt.hist(x, bins=30)
  plt.show()

  x = [random_gaussian_expect(10, vmin=3) for _ in tqdm(range(300))]
  plt.hist(x, bins=30)
  plt.show()

  random_choice([i for i in range(11)])
