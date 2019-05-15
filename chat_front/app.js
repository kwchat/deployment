var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io').listen(server);
const axios = require('axios');
var apiai = require('apiai');
var ai = apiai("664548d3292b4d9697a5d5e7fb093a81");

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
        console.log('일루 들어옴')
        var request = ai.textRequest(data, {
            sessionId: 'kw-chatbot'
        });
        request.on('response', function(response) {
            console.log('??? : ', response);
            var res = response.result.fulfillment.speech // dialogflow의 답변

            var url = encodeURI('http://localhost:5000/?message='+data)
            axios.get(url)
            .then(function (response) {
                res = response.data; // wiki 또는 seq2seq로부터 온 답변

                console.log("hahahahahaha : ", res)

                // 답변이 wiki로부터 왔다면
                    // 온거 뱉기

                // 답변이 seq2seq로부터 왔다면 그리고 dialogflow 답변이 aaa가 아니라면
                    // dialog뱉기

                // 둘다 아니라면
                    // 온거 뱉기
                    
                io.sockets.emit('bot message', res)
            })
            .catch(function (error) {
                // handle error
                console.log(error);
            })
        });
        request.on('error', function(error) {
            console.log(error);
        });
        
        request.end();
    });
});
