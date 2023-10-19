### game:join 加入游戏

点击开始游戏后，等待双方确认

```typescript
// request
interface {
  rid: int    // 房间号
  r: int      // 选择比特值用以初始化
}

// response
interface {

}
```

### game:start 游戏开始

待双方确认后，初始化游戏状态

```typescript
// emit
interface {
  // Game 结构
}
```

### game:settle 游戏结束

服务器模拟达到触发条件后，主动通知客户端结束游戏

```typescript
// emit
interface {
  winner: string
  endTs: int
}
```
