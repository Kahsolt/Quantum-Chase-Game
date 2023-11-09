#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/20

from numpy import pi


# 刷新帧率
FPS = 30

# 角色名
ALICE = 'Alice'
BOB   = 'Bob'

# 角色对应 qubit 索引 (两qubit线路中)
QUBIT_MAP = {
  ALICE: 0,
  BOB:   1,
}

# 角色移动角速度: 假设 60s 转一圈
MOVE_SPEED = 2 * pi / 60 * 3

# 角色拾取范围
PICK_RADIUS = 0.06

# 物品生成速度
SPAWN_INTERVAL = 15

# 物品生成数量上限
SPAWN_LIMIT = 30

# 物品生成的份数期望
SPAWN_COUNT_PHOTON = 37
SPAWN_COUNT_GATE = 1.5

# 物品存活时间期望中心
SPAWN_TTL = 90

# 物品生成权重
SPAWN_WEIGHT = {
  'photon': 500,
  'X': 10,
  'Y': 10,
  'Z': 10,
  'H': 10,
  'S': 10,
  'T': 10,
  'X2P': 20,
  'X2M': 20,
  'Y2P': 20,
  'Y2M': 20,
  'CNOT': 10,
  'SWAP': 5,
  'RX': 5,
  'RY': 5,
  'RZ': 5,
  'M': 5,
}

# 纬线圈提示时间
LOC_QUERY_TTL = 10

# 自动解除纠缠的时间
DETGL_TTL = 15

# 门操作计算噪声 (not used)
ENV_NOISE = 0.0
