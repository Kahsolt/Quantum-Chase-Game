#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/11/06

from modules.assets import *
from .utils import *

colors_warm = (
  # flame start colors
  Vec4(1.0, 0.0, 0.0, 1.0),
  Vec4(1.0, 0.2, 0.0, 1.0),
  Vec4(1.0, 0.7, 0.0, 1.0),
  Vec4(0.0, 0.0, 0.2, 1.0),
  # flame end color
  Vec4(1.0, 1.0, 0.0, 1.0),
)

colors_cold = (
  # flame start colors
  Vec4(0.0, 0.0, 1.0, 1.0),
  Vec4(0.0, 0.2, 1.0, 1.0),
  Vec4(0.0, 0.7, 1.0, 1.0),
  Vec4(0.2, 0.0, 0.0, 1.0),
  # flame end color
  Vec4(0.0, 1.0, 1.0, 1.0),
)


def make_trail(loader:Loader, parent:NodePath, obj:NodePath, flame_colors:List[Vec4], length:int=3, width:float=5.0) -> Prefab:
  texture = loader.loadTexture(TX_PLASMA)
  
  trail = MotionTrail('trail', obj)
  trail.register_motion_trail()
  trail.geom_node_path.reparentTo(parent)
  trail.set_texture(texture)
  trail.time_window = length

  # A circle as the trail's shape, by plotting a NodePath in a circle.
  center = parent.attachNewNode('center')
  around = center.attachNewNode('around')
  around.setZ(1)

  # Amount of angles in 'circle'. Higher is smoother.
  res = 4
  for i in range(res + 1):
    center.setR((360 / res) * i)
    vertex_pos = around.getPos(parent)
    trail.add_vertex(vertex_pos)

    start_color = flame_colors[i % (len(flame_colors) - 1)] * 1.7
    end_color = flame_colors[-1]
    trail.set_vertex_color(i, start_color, end_color)
  trail.update_vertices()

  anims = [
    # Adding intervals to the trail to give it swoops and bends.
    LerpHprInterval(trail, 2, (0, 0, -360)),
    LerpTexOffsetInterval(trail.geom_node_path, 4, (1, 1), (1, 0)),
    # Grow and shrink
    Sequence(
      LerpScaleInterval(trail, 0.3, width, 1.0, blendType='easeInOut'),
      LerpScaleInterval(trail, 0.5, 1.0, width, blendType='easeInOut'),
    ),
  ]

  return (trail,), anims
