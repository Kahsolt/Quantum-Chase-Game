### item:spawn 地图上自然生成事物

进行房间广播

```typescript
// emit
interface {
  item: {
    type: str
    id: str
    count?: int
  }
  loc: [int, int]
  ttl: int        // 消失时间
  ts: int         // 出生时间
}
```

### item:pick 玩家捡东西

```typescript
// request 
interface {

}

// response
interface {
  type: str
  id: str
  count: int
}
```
