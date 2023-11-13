#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/10/20

from numpy import pi


# object 产生接触的距离
FID_TOUCH = 0.9995

# 游戏限时: Alice胜利条件
TIME_LIMIT = 60 * 5

# 游戏倒计时结束前提示 fid 的时间
SHOW_FID_TTL = 60

# 抓住距离: Bob胜利条件
CATCH_FID = 0.998

# 双方可见的距离
VISIBLE_FID = 0.95   # 相距 4 倍 object 大小

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

# 角色移动角速度: 假设 60s 转一圈
MOVE_SPEED = 2 * pi / 60 * 3

# 角色拾取范围
PICK_FID = FID_TOUCH

# 物品生成速度
SPAWN_INTERVAL = 7

# 物品生成同时存在数量上限
SPAWN_LIMIT = 30

# 物品生成的份数期望
SPAWN_COUNT_PHOTON = 57
SPAWN_COUNT_GATE = 1.5

# 物品存活时间期望中心
SPAWN_TTL = 55

# 物品生成权重
SPAWN_WEIGHT = {
  'photon': 200,
  'theta': 60,      # should equal to p-rot gates
  'X': 5,
  'Y': 5,
  'Z': 5,
  'H': 20,
  'S': 10,
  'T': 20,
  'X2P': 10,
  'Y2P': 10,
  'CNOT': 10,
  'SWAP': 5,
  'RX': 20,
  'RY': 20,
  'RZ': 20,
  'M': 5,
}

# 纬线圈提示时间
LOC_QUERY_TTL = 10

# 自动解除纠缠的时间 (not used)
DETGL_TTL = 15

# 门操作计算噪声 (not used)
ENV_NOISE = 0.0
