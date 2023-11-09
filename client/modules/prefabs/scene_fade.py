#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from .utils import *


def make_scene_fade_anims(scene:NodePath) -> Anims:
  in_anim = Parallel(
    LerpColorInterval(scene, 1.2, WHITE, blendType='noBlend'),
    LerpColorScaleInterval(scene, 1.2, WHITE, WHITE_0, blendType='noBlend'),
  )
  out_anim = Parallel(
    LerpColorInterval(scene, 1.2, WHITE, blendType='noBlend'),
    LerpColorScaleInterval(scene, 1.2, WHITE_0, WHITE, blendType='noBlend')
  )
  return in_anim, out_anim
