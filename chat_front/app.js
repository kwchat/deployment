var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io').listen(server);
const axios = require('axios');

users = [];
connections = [];

server.listen(process.env.PORT || 3000);

app.use(express.static(__dirname));
app.get('/', function(req, res){
    res.sendFile(__dirname + '/index.html');
})

io.sockets.on('connection', function(socket){
    connections.push(socket);
    console.log('connected: %s sockets connected', connections.length);
    
    socket.on('disconnect', function(data){
        connections.splice(connections.indexOf(socket), 1);
        console.log('Disconnected: %s sockets connected', connections.length);
    })

    socket.on('send message', function(data){
        console.log(data);
        io.sockets.emit('new message', {msg: data});
    });

    socket.on('send message', function(data){   
        var url = encodeURI('http://localhost:5000/?message='+data)
        axios.get(url)
        .then(function (response) {
          // handle success
          console.log(response);
          io.sockets.emit('bot message', response.data)

        })
        .catch(function (error) {
          // handle error
          console.log(error);
        })
    });
});
