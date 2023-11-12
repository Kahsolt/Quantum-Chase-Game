# API documentation

=> Data Model: [/data](/data)

### General

Serving game logic through **Websocket** protocol  
The payload for both requests and responses are in **JSON** format  
All event names (alike HTTP routes) are RESTful-like designed  

The common JSON fields for all packets:

```typescript
// request
interface {

}

// response (success)
interface {
  ok: bool = true     // success status
  data: dict|list     // data payload
  ts: timestamp       // server current time
}
// response (failed)
interface {
  ok: bool = false    // failed status
  error: str          // error messag
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
  rid: str       // 房间名
  r: int         // 玩家选择比特值用以开局
}

// response
interface { }
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
// emit (broadcast)
interface {
  winner: string    // 角色id
  endTs: int
}
```

#### game:sync 全量数据同步

```typescript
// request
interface { }

// response
interface {
  // Game 结构
}
```

#### game:ping 心跳

```typescript
// request
interface { }

// response
interface { }
```

#### mov:start 移动开始/改变

玩家按下/半释放方向键

```typescript
// request
interface {
  dir: int
  spd?: int
}

// response (broadcast)
interface {
  id: string
  dir: int      // 复制自 request
  spd?: int
}
```

#### mov:stop 停止移动

玩家完全释放方向键

```typescript
// request 
interface { }

// response (broadcast)
interface {
  [id: string]: [int, int]    // 各玩家位置 (被动误差修正用)
}
```

#### loc:query 查询位置

消耗光子，测量隐形传态的结果，查询对方玩家位置信息

```typescript
// request
interface {
  photons: int         // 消耗光子数量
  basis: 'Z' | 'X'    // 测量的基 (目前只支持Z)
}

// response
interface {
  freq: [int, int]    // 测量结果频度分布列
  photons: int
}
```

#### loc:sync 同步位置

获取服务端计算的各玩家当前位置 (主动误差修正用)

```typescript
// request
interface { }

// response
interface {
  [id: string]: [int, int]    // 各玩家位置
}
```

#### item:spawn 地图上事物生成

```typescript
// emit (broadcast)
interface {
  ts: int         // 出生时间, use as uid
  ttl: int        // 生存时长
  loc: [int, int]
  item: {
    type: str
    id: str
    count: int
  }
}
```

#### item:vanish 地图上事物消失 (超时/被捡)

```typescript
// emit (broadcast)
interface {
  ts: int   // use as uid
}
```

#### item:pick 玩家捡生成物

依服务端计算的玩家所在位置为准

```typescript
// request 
interface {
  ts: int   // use as uid
}

// response
interface { }   // 空返回，会触发 item:gain
```

#### item:gain 玩家获得道具

```typescript
// emit 
interface {
  // Item 结构
}
```

#### item:cost 玩家消耗道具

```typescript
// emit 
interface {
  // Item 结构
}
```

#### gate:rot 给自己施加单比特旋转门

```typescript
// request
interface {
  gate: str
}

// response
interface {     // 非纠缠
  [id: string]: [int, int]    // 各玩家位置
}
// response (broadcast)
interface {     // 纠缠
  state: [float] * 8          // 4个复数
}
```

#### gate:swap 施加 SWAP 门，交换双方玩家的态

```typescript
// request
interface { }

// response (broadcast)
interface {
  [id: string]: [int, int]    // 各玩家位置
}
```

#### gate:cnot 施加 CNOT 门，产生全局纠缠

进行房间广播

```typescript
// request 
interface { }

// response
interface {
  state: [float] * 8          // 4个复数
}
```

#### gate:meas 测量自己 / 主动解除全局纠缠态

```typescript
// request 
interface { }

// response
interface {
  [id: string]: [int, int]    // 各玩家位置
}
```

#### entgl:freeze 进入全局纠缠态

通知客户端冻结 mov 和 loc 模块

```typescript
// emit (broadcast)
interface { }
```

#### entgl:break 解除全局纠缠态

通知客户端冻结 mov 和 loc 模块

```typescript
// emit (broadcast)
interface { }
```

----

### Debug

=> websocket test page: [/ws](/ws)
=> runtime info: [/info](/info)

----

<p> by Armit <time> 2023/10/16 </time> </p>
