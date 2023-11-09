# Data Model

=> API doc: [/api](/api)

----

⚠ 出于帧同步的要求，所有可变量的 float 类型数据都统一放大为 int 类型以进行网络传输


⚪ Playerdata

```typescript
interface Game {
  me: string                // 我的角色 id
  players: {                // 各玩家
    [id: string]: Player
  }
  entgl: bool               // 是否处于全局纠缠态
  winner: string            // 游戏胜利方角色
  startTs: timestamp        // 游戏开始时间
  endTs: timestamp          // 游戏结束时间
}

interface Player {
  dir: int | null           // 移动弧度方向 dir (枚举值 0~7)
  spd: int                  // 移动秒角速度 spd
  loc: [int, int]           // bloch球面位置 (tht, psi)
  photons: int              // 光子 (道具)
  gates: {                  // 量子门 (道具)
    [name: string]: int
  }
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
  loc: [int, int]   // 出生位置
  ttl: int          // 生存时长
  ts: int           // 出生时刻
}
```

----

<p> by Armit <time> 2023/10/16 </time> </p>
