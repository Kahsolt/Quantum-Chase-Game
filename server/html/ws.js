const socket = io();
console.log(socket);

socket.on('connect', () => {
  socket.emit('my event', {data: 'connected!'});
});

socket.on('my response', (resp) => {
  console.log('response:', resp);
});

socket.emit('my function', {data: [1, 2]});
