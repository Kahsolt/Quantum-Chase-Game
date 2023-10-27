### mov:start 移动开始/改变

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

### mov:stop 停止移动

玩家完全释放方向键，进行房间广播

```typescript
// request 
interface {

}

// response
interface {
  id: string
  loc: [int, int]   // 服务端计算的玩家位置
}
```

### mov:freeze 冻结移动键

```typescript
// emit
interface {

}
```

### mov:unfreeze 解冻移动键

```typescript
// emit
interface {

}
```

### loc:query 查询位置

消耗光子，测量隐形传态的结果，查询对方玩家

```typescript
// request
interface {
  photon: int
}

// response
interface {
  freq: [int, int]    // 测量结果频度分布列
}
```

### loc:sync 同步位置

获取服务端计算的各玩家当前位置 (位置公布以后，误差修正用)

```typescript
// request
interface {

}

// response
interface {
  [id: string]: [int, int]    // 服务端计算的各玩家的位置
}
```
