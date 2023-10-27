### gate:rot 给自己施加单比特旋转门

若为全局纠缠态/双方可见，进行房间广播；否则点对点回复

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

### gate:swap 全局施加 SWAP 门，交换双方玩家的态

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

### gate:cnot 全局施加 CNOT 门，产生全局纠缠

进行房间广播

```typescript
// request 
interface {

}

// response
interface {
  state: [int, int, int, int]   // 实/虚/实/虚
}
```

### gate:meas 测量自己 / 解除全局纠缠态

进行房间广播

```typescript
// request 
interface {

}

// response
interface {   // 测量自己
  id: string
  loc: [int, int]
}
interface {   // 解除纠缠态
  [id: string]: [int, int]    // loc
}
```
