#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/20

from numpy import pi


# object 产生接触的距离
FID_TOUCH = 0.9995

# 游戏限时: Alice胜利条件
TIME_LIMIT = 60 * 3 + 40

# 游戏倒计时结束前提示 fid 的时间
SHOW_FID_TTL = 60

# 抓住距离: Bob胜利条件
CATCH_FID = 0.998

# 双方可见的距离
VISIBLE_FID = 0.95   # 相距约 4 倍 object 大小

# 刷新帧率
FPS = 30

# 心跳间隔
HEART_BEAT = 10

# 角色名
ALICE = 'Alice'
BOB   = 'Bob'

# 角色对应 qubit 索引 (两qubit线路中)
QUBIT_MAP = {
  ALICE: 0,
  BOB:   1,
}

# 角色移动角速度: 假设 20s 转一圈
MOVE_SPEED = 2 * pi / 60 * 3

# 角色拾取范围
PICK_FID = 0.9993

# 初始道具
INIT_PHOTON = 300
INIT_THETA = 3
INIT_GATE = {
  'X': 2,
  'Y': 2,
  'Z': 2,
  'H': 3,
  'S': 2,
  'T': 2,
  'X2P': 2,
  'Y2P': 2,
  'RX': 1,
  'RY': 1,
  'RZ': 1,
  'CNOT': 1,
}

# 物品生成速度
SPAWN_INTERVAL = 5

# 物品生成同时存在数量上限
SPAWN_LIMIT = 42

# 物品生成的份数期望
SPAWN_COUNT_PHOTON = 57
SPAWN_COUNT_THETA = 2
SPAWN_COUNT_GATE = 2

# 物品存活时间期望中心
SPAWN_TTL = 55

# 物品生成权重
SPAWN_WEIGHT = {
  'photon': 100,
  'theta': 60,      # should equal to p-rot gates
  'X': 5,
  'Y': 5,
  'Z': 5,
  'H': 20,
  'S': 10,
  'T': 20,
  'X2P': 10,
  'Y2P': 10,
  'CNOT': 20,
  'SWAP': 5,
  'RX': 20,
  'RY': 20,
  'RZ': 20,
  'M': 5,
}

# 纬线圈提示时间
LOC_QUERY_TTL = 10

# 自动解除纠缠的时间
DETGL_TTL = 15

# 门操作计算噪声
ENV_NOISE = 0.1

# 噪声变化间隔
NOISE_CHANGE_INTERVAL = 30


if __name__ == '__main__':
  keys = list(SPAWN_WEIGHT.keys())
  values = list(SPAWN_WEIGHT.values())
  total = sum(values)
  probs = [e / total for e in values]
  for k, v in zip(keys, probs):
    print(f'{k}: {v:.3%}')
