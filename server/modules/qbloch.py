#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/13

# utils converting GUI repr to isQ repr

from qlocal import Prob
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
  amp = np.asarray([complex(p, q), complex(r, s)], dtype=np.complex64)
  amp /= np.linalg.norm(amp)    # unit vector
  return emit_gphase(amp.tolist())

def emit_gphase(phi:Phi) -> Phi:
  '''
    Euler's formula: e^ix = cos(x) + i * sin(x)
    for arbitary |phi> = a|0> + b|1>, multiply by the unit vector `a.conj / |a|` will 
    force coeff on |0> become a real number: `a*a.conj/|a|`, while not changing th amplitude balance
  '''
  a, b = phi
  mult = a.conjugate() / abs(a)
  a = (a * mult).real
  b = b * mult
  if a < 0: a, b = -a, -b
  return a, b

def clock_angle(x:float) -> float:
  return x + (2 * pi if x < 0 else 0)

def phi2prob(phi:Phi) -> Prob:
  return [abs(e)**2 for e in phi]


# geo-mapping see: https://en.wikipedia.org/wiki/Bloch_sphere
def loc2phi(loc:Loc) -> Phi:
  ''' |phi> = cos(θ/2)|0> + e^(iφ)sin(θ/2)|1> '''
  tht, psi = loc
  assert 0 <= tht <= pi, f'`tht` should be in range [0, pi], but got {tht}'
  assert 0 <= psi <= 2*pi, f'`psi` should be in range [0, 2*pi], but got {psi}'
  return np.cos(tht / 2), np.exp(psi*1j) * np.sin(tht / 2)

def phi2loc(phi:Phi) -> Loc:
  ''' |phi> = a|0> + b|1> => (tht, phi)'''
  a, b = emit_gphase(phi)
  tht = 2 * np.arccos(a)
  tht = clock_angle(tht)
  psi = np.log(b / np.sin(tht / 2) + 1e-15).imag
  psi = clock_angle(psi)
  assert 0 <= tht <= pi, f'`tht` should be in range [0, pi], but got {tht}'
  assert 0 <= psi <= 2*pi, f'`psi` should be in range [0, 2*pi], but got {psi}'
  return tht, psi


if __name__ == '__main__':
  equal = lambda x, y: np.all(np.abs(np.asarray(x) - np.asarray(y)) < 1e-5)

  loc = rand_loc()
  print('loc:    ', loc)
  print('loc2phi:', loc2phi(loc))
  loc_rev = phi2loc(loc2phi(loc))
  print('loc_rev:', loc_rev)
  assert equal(loc, loc_rev)

  phi = rand_phi()
  print('phi:    ', phi)
  print('phi2loc:', phi2loc(phi))
  phi_rev = loc2phi(phi2loc(phi))
  print('phi_rev:', phi_rev)
  assert equal(phi, phi_rev)
