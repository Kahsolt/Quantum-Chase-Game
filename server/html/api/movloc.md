### mov:change 移动开始/改变

玩家按下/半释放方向键，进行房间广播

```typescript
// request / response
interface {
  id: string
  dir: int
  spd?: float
}
```

### mov:stop 停止移动

玩家完全释放方向键，进行房间广播

```typescript
// request 
interface {
  id: string
}

// response
interface {
  id: string
  loc: [float, float]   // 服务端计算的玩家位置
}
```

### loc:sync 同步位置

获取服务端计算的当前位置 (并强制更新)

```typescript
// request
interface {

}

// response
interface {
  [id: string]: [float, float]    // 服务端计算的各玩家的位置
}
```
