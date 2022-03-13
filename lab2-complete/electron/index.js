document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "10.0.0.116";   // the IP address of your Raspberry PI

function send_data(data) {
    const net = require('net');
    //var input = document.getElementById("message").value;

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        //console.log(data.toString());
        // send the message
        client.write(`${data}\r\n`);
    });



}
function client(){
    
    const net = require('net');
    //var input = document.getElementById("message").value;

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        client.write(`data\r\n`);
    });
    
    // get the data from the server
    client.on('data', (data) => {
        const obj = JSON.parse(data);
        document.getElementById("direction").textContent = obj.direction;
        document.getElementById("temperature").textContent = obj.temperature;
        document.getElementById("battery_level").textContent = obj.battery_level;
        //console.log(data.toString());
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data("forward");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data("backward");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data("left");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data("right");
    }
    else if (e.keyCode == '32') {
        // right (d)
        document.getElementById("stopSymbol").style.color = "green";
        send_data("stop");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
    document.getElementById("stopSymbol").style.color = "grey";
}


// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}
