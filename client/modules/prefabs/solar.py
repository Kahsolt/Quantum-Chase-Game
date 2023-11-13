#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from modules.assets import *
from .utils import *


def make_solar(loader:Loader, parent:NodePath, name:str, color:Vec4, offsetX:int) -> Prefab:
  model = loader.loadModel(MO_SPHERE)
  texture = loader.loadTexture(TX_PLASMA)

  # A self-rotating fixed star in empty space.
  star = parent.attachNewNode(name)

  # A planet offset to the star
  planet = star.attachNewNode('planet')
  planet.setX(offsetX)

  # A satellite offset to the planet
  satellite = model.copyTo(planet)
  satellite.setTexture(texture)
  satellite.setColor(color * 1.2)
  satellite.setTransparency(TransparencyAttrib.MAlpha)
  satellite.setScale(0.5)
  satellite.setX(1.2)

  objs = star, planet, satellite

  anims = [
    # self-rotation
    LerpHprInterval(star,    3, (360, 0, 0)),
    LerpHprInterval(planet, 10, (360, 0, 0)),
    # vibrate along z-axis (near-far)
    Sequence(
      LerpPosInterval(star, 0.3, (0, 0, -3), (0, 0,  1), blendType=IN),
      LerpPosInterval(star, 0.5, (0, 0,  1), (0, 0, -3), blendType=OUT),
    ),
  ]

  return objs, anims
