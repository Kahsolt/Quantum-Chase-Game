#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from .utils import *


def make_scene_fade_anims(scene:NodePath) -> Anims:
  in_anim = Parallel(
    LerpColorInterval(scene, 1.2, Vec4(1, 1, 1, 1), blendType='noBlend'),
    LerpColorScaleInterval(scene, 1.2, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0), blendType='noBlend'),
  )
  out_anim = Parallel(
    LerpColorInterval(scene, 1.2, Vec4(1, 1, 1, 1), blendType='noBlend'),
    LerpColorScaleInterval(scene, 1.2, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1), blendType='noBlend')
  )
  return in_anim, out_anim
