#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

# utils converting GUI repr to isQ repr

from utils import *

Loc = Tuple[float, float]
Phi = Tuple[complex, complex]

randpi = lambda: rand() * pi              # random [0, pi)
randnpi = lambda: (rand() * 2 - 1) * pi   # random [-pi, pi)


def rand_loc() -> Loc:
  ''' (θ, φ); θ in [0, pi], φ in [0, 2*pi] '''
  return randpi(), randpi() * 2

def rand_phi() -> Phi:
  ''' |phi> = (p+qi)|0> + (r+si)|1> '''
  p, q, r, s = randnpi(), randnpi(), randnpi(), randnpi()
  return complex(p, q), complex(r, s)


# geo-mapping see: https://en.wikipedia.org/wiki/Bloch_sphere
def loc2phi(loc:Loc) -> Phi:
  ''' |phi> = cos(θ)|0> + e^(iφ)|1> '''
  tht, phi = loc
  assert 0 <= tht <= pi, f'`tht` should be in range [0, pi], but got {tht}'
  assert 0 <= phi <= 2*pi, f'`phi` should be in range [0, 2*pi], but got {phi}'
  return np.cos(tht), np.exp(phi*1j)

def phi2loc(phi:Phi) -> Loc:
  ''' |phi> = a|0> + b|1> => (tht, phi)'''
  # TODO: 你妈的，这个由于全局相位导致不唯一？？
  a, b = phi
  tht = 2 * np.arccos(a)
  psi = np.log(b / np.sin(tht / 2) + 1e-15) / 1j
  return tht, psi


if __name__ == '__main__':
  loc = rand_loc()
  print('loc:', loc)
  print('loc2phi:', loc2phi(loc))

  phi = rand_phi()
  print('phi:', phi)
  print('phi2loc:', phi2loc(phi))
