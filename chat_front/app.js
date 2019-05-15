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
            var res_dialog = response.result.fulfillment.speech // dialogflow의 답변

            var url = encodeURI('http://localhost:5000/?message='+data)
            axios.get(url)
            .then(function (response) {
                res_data = response.data.data; // wiki 또는 seq2seq로부터 온 답변
                res_class = response.data.intent_class;

                if(res_class == 'what'){ // wiki
                    io.sockets.emit('bot message', res_data)
                }

                else if(res_class == 'others' && res_dialog != 'aaa'){ // dialog
                    io.sockets.emit('bot message', res_dialog)
                }
                
                else{ // seq2seq
                    io.sockets.emit('bot message', res_data)
                }            
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
