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
  // 移动弧度方向 dir
  dir: float | null
  // 移动秒角速度 spd
  spd: float | null
  // bloch球面位置 (tht, psi)
  loc: [float | null, float | null]
  bag: {                  // 背包
    photon: int           // 光子 (代币)
    gate: {               // 量子门 (道具)
      [name: string]: int
    } | null
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
