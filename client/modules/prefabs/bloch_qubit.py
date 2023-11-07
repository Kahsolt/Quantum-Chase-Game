#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from modules.assets import *
from .utils import *

from .trail import make_trail, colors_cold, colors_warm


def make_bloch_qubits(loader:Loader, parent:NodePath) -> Prefab:
  blochNP = loader.loadModel(MO_SPHERE_HIGHPOLY).copyTo(parent)
  blochNP.setTexture(loader.loadTexture(TX_PLASMA))
  blochNP.setTransparency(TransparencyAttrib.MAlpha)
  blochNP.setColor(1.0, 1.0, 1.0, 0.9)
  blochNP.setScale(1)

  # Alice
  qubit1NP = loader.loadModel(MO_SPHERE).copyTo(blochNP)
  qubit1NP.setTextureOff()
  qubit1NP.setTransparency(TransparencyAttrib.MAlpha)
  qubit1NP.setColor(colors_cold[0])
  qubit1NP.setPos(0, -3.3, 0)
  qubit1NP.setScale(0.02)

  # Bob
  qubit2NP = loader.loadModel(MO_SPHERE).copyTo(blochNP)
  qubit2NP.setTextureOff()
  qubit2NP.setTransparency(TransparencyAttrib.MAlpha)
  qubit2NP.setColor(colors_warm[0])
  qubit2NP.setPos(0, -3.3, 0)
  qubit2NP.setScale(0.02)

  objs1, anims1 = make_trail(loader, parent, qubit1NP, colors_cold, length=1, width=2.0)
  objs2, anims2 = make_trail(loader, parent, qubit2NP, colors_warm, length=1, width=2.0)

  return (blochNP, qubit1NP, qubit2NP), (anims1 + anims2)
