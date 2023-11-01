# Playerdata documentation

=> API doc: [/api](/api)

----

⚠ 出于帧同步的要求，所有 float 类型都统一放大为 int 类型以进行网络传输


⚪ Playerdata

```typescript
interface Game {
  me: string                              // 我的角色
  players: Record<string/*id*/, Player>   // 各玩家状态
  winner: string                          // 游戏胜利方角色
  startTs: timestamp                      // 游戏开始时间
  endTs: timestamp                        // 游戏结束时间
  noise: float                            // 量子计算噪声
}

interface Player {
  // 移动弧度方向 dir (枚举值 0~7)
  dir: int | null
  // 移动秒角速度 spd
  spd: int | null
  // bloch球面位置 (tht, psi)
  loc: [int | null, int | null]
  // 光子 (道具)
  photon: int
  // 量子门 (道具)
  gate: {
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
  loc: [int, int] 
  ttl: int          // 生存时长
  ts: int           // 出生时间
}
```

----

<p> by Armit <time> 2023/10/16 </time> </p>
