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

<ul>
{% for page in pages %}
  <li><a href="/api/{{page}}"> {{page}} </a></li>
{% endfor %}
</ul>

----

### Debug

=> websocket test page: [/ws](/ws)
=> runtime info: [/info](/info)

----

<p> by Armit <time> 2023/10/16 </time> </p>
