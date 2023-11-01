# API documentation

=> playerdata doc: [/doc](/doc)

### General

Serving game logic through **Websocket** protocol  
The payload for both requests and responses are in **JSON** format  
All event names (alike HTTP routes) are RESTful-like designed  

The common JSON fields for all packets:

```typescript
// request
interface {

}

// response
interface {
  ok: bool            // success status
  data?: list|dict    // data payload
  error?: str         // error message
  ts: timestamp       // server current time
}
```

----

### APIs

#### game:join 加入游戏

点击开始游戏后，等待双方确认

```typescript
// request
interface {
  rid: int    // 房间号
  r: int      // 选择比特值用以初始化
}

// response
interface { }
```

#### game:sync 同步 player 部分的数据

```typescript
// request
interface { }

// response
interface {
  // Player 结构
}
```

#### game:start 游戏开始

待双方确认后，初始化游戏状态

```typescript
// emit
interface {
  // Game 结构
}
```

#### game:settle 游戏结束

服务器模拟达到触发条件后，主动通知客户端结束游戏

```typescript
// emit
interface {
  winner: string
  endTs: int
}
```

#### mov:start 移动开始/改变

玩家按下/半释放方向键，进行房间广播

```typescript
// request
interface {
  dir: int
  spd?: int
}

// response
interface {
  id: string
  dir: int      // 复制 request
  spd?: int
}
```

#### mov:stop 停止移动

玩家完全释放方向键，进行房间广播

```typescript
// request 
interface { }

// response
interface {
  id: string
  loc: [int, int]   // 服务端计算的玩家位置，用于修正
}
```

#### loc:query 查询位置

消耗光子，测量隐形传态的结果，查询对方玩家

```typescript
// request
interface {
  photon: int         // 消耗光子数量
  basis: 'Z' | 'X'    // 测量的基
}

// response
interface {
  freq: [int, int]    // 测量结果频度分布列
}
```

#### loc:sync 同步位置

获取服务端计算的各玩家当前位置 (位置公布以后，误差修正用)

```typescript
// request
interface { }

// response
interface {
  [id: string]: [int, int]    // 服务端计算的各玩家的位置
}
```

#### item:spawn 地图上自然生成事物

进行房间广播

```typescript
// emit
interface {
  item: {
    type: str
    id: str
    count: int
  }
  loc: [int, int]
  ttl: int        // 生存时长
  ts: int         // 出生时间
}
```

#### item:pick 玩家捡东西

依服务端计算的位置为准

```typescript
// request 
interface { }

// response
interface {
  type: str
  id: str
  count: int
}
```

#### gate:rot 给自己施加单比特旋转门

若为全局纠缠态，进行房间广播；否则点对点回复

```typescript
// request
interface {
  gate: str
}

// response
interface {     // 非纠缠的情况
  id: string
  loc: [int, int]
}
interface {     // 纠缠的情况
  state: [int, int, int, int]   // 实/虚/实/虚
}
```

#### gate:swap 施加 SWAP 门，交换双方玩家的态

进行房间广播

```typescript
// request
interface {
  photon: int
}

// response
interface {
  [id: string]: [int, int]    // loc
}
```

#### gate:cnot 施加 CNOT 门，产生全局纠缠

进行房间广播

```typescript
// request 
interface { }

// response
interface {
  state: [(int, int), (int, int), (int, int), (int, int)]   // 四项复数振幅
}
```

#### gate:meas 测量自己 / 主动解除全局纠缠态

```typescript
// request 
interface { }

// response
interface {   // 测量自己，点对点
  id: string
  loc: [int, int]
}
interface {   // 解除纠缠态，进行房间广播
  [id: string]: [int, int]    // loc
}
```

#### entgl:freeze 进入全局纠缠态

主动房间广播，客户端应该冻结 自由移动 和 位置探测 功能

```typescript
// emit
interface { }
```

#### entgl:break 解除全局纠缠态

主动房间广播，客户端应该解冻 自由移动 和 位置探测 功能

```typescript
// emit
interface { }
```

----

#### service:api 样例服务样例指令

⚪ 客户端请求

```typescript
// request
interface {
  val: float
}

// response
interface {
  val: float
}
```

⚪ 服务端推送

```typescript
// emit
interface {
  val: float
}
```

----

### Debug

=> websocket test page: [/ws](/ws)
=> runtime info: [/info](/info)

----

<p> by Armit <time> 2023/10/16 </time> </p>
