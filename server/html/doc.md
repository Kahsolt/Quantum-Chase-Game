# Playerdata documentation

=> API doc: [/api](/api)

----

```typescript
interface Game {
  me: string
  players: Record<string/*id*/, Player>
  status: Status
  const: Const
}

interface Player {
  loc: [float, float]     // 球面位置坐标 (tht, psi)
  mov: {                  // 移动
    dir: float            // 方向
    spd: float            // 速度
  }
  bag: {                  // 背包
    photon: int           // 光子 (代币)
    gate: {               // 量子门 (道具)
      [name: string]: int
    }
  }
}

interface Status {
  stage: int              // 游戏目标阶段
  winner: string
  startTs: timestamp
  endTs: timestamp
}

interface Const {
  cost: Record<string, int>   // 消耗量子门需要花费光子
  noise: float                // 量子计算噪声
}
```

----

<p> by Armit <time> 2023/10/16 </time> </p>
