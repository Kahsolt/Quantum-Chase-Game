# Playerdata documentation

=> API doc: [/api](/api)

----

⚪ Playerdata

```typescript
interface Game {
  me: string
  players: Record<string/*id*/, Player>
  status: Status
  const: Const
}

interface Player {
  // 移动弧度方向 dir (枚举值 0~7)
  dir: int | null
  // 移动秒角速度 spd
  spd: int | null
  // bloch球面位置 (tht, psi)
  loc: [int | null, int | null]
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

⚪ Item

```typescript
interface Item {
  type: ItemType
  id: ItemId
  count: int
}

interface SpawnItem {
  item: Item
  loc: [float, float] 
  ttl: int
  ts: int
}
```

----

<p> by Armit <time> 2023/10/16 </time> </p>
