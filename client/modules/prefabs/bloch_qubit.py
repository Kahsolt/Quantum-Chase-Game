#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from modules.assets import *
from modules.ui_configs import *

from .utils import *


def make_bloch_qubits(loader:Loader, parent:NodePath):
  # bloch sphere
  blochNP = loader.loadModel(MO_SPHERE_HIGHPOLY).copyTo(parent)
  blochNP.setTexture(loader.loadTexture(TX_PLASMA))
  blochNP.setTransparency(TransparencyAttrib.MAlpha)
  blochNP.setColor(1, 1, 1, BLOCH_ALPHA)
  blochNP.setR(BLOCH_SLOPE)
  blochNP.setScale(BLOCH_SIZE)

  # axis X
  lines = LineSegs()
  lines.setThickness(AXIS_THICKNESS)
  lines.setColor(0.7, 0, 0, 0.7)
  lines.moveTo(0, 0, 0)
  lines.drawTo(+10, 0, 0)
  lines.drawTo(-10, 0, 0)
  axisNP = NodePath(lines.create())
  axisNP.setTextureOff()
  axisNP.reparentTo(blochNP)

  # axis Y
  lines = LineSegs()
  lines.setThickness(AXIS_THICKNESS)
  lines.setColor(0, 0.7, 0, 0.7)
  lines.moveTo(0, 0, 0)
  lines.drawTo(0, +10, 0)
  lines.drawTo(0, -10, 0)
  axisNP = NodePath(lines.create())
  axisNP.setTextureOff()
  axisNP.reparentTo(blochNP)

  # axis Z
  lines = LineSegs()
  lines.setThickness(AXIS_THICKNESS)
  lines.setColor(0.0, 0, 0.7, 0.7)
  lines.moveTo(0, 0, 0)
  lines.drawTo(0, 0, +10)
  lines.drawTo(0, 0, -10)
  axisNP = NodePath(lines.create())
  axisNP.setTextureOff()
  axisNP.reparentTo(blochNP)

  # qubit Alice
  qubit1NP = loader.loadModel(MO_SPHERE).copyTo(blochNP)
  qubit1NP.setTextureOff()
  qubit1NP.setTransparency(TransparencyAttrib.MAlpha)
  qubit1NP.setColor(*QUBIT_COLOR_ALICE)
  qubit1NP.setPos(0, QUBIT_OFFSET, 0)
  qubit1NP.setScale(QUBIT_SIZE)

  # qubit Bob
  qubit2NP = loader.loadModel(MO_SPHERE).copyTo(blochNP)
  qubit2NP.setTextureOff()
  qubit2NP.setTransparency(TransparencyAttrib.MAlpha)
  qubit2NP.setColor(*QUBIT_COLOR_BOB)
  qubit2NP.setPos(0, QUBIT_OFFSET, 0)
  qubit2NP.setScale(QUBIT_SIZE)

  return (blochNP, qubit1NP, qubit2NP), []
