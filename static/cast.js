var socket, peer, currentStream, projector;

function cast() {
    if (/Mobi/.test(navigator.userAgent)) {
        alert("Proyectar la pantalla no es compatible con dispositivos móviles.\n\nSe recomienda usar un ordenador Windows o Apple con Chrome, Edge o Safari.");
        return;
    }
    uncast();
    var constraints = {
        audio: false,
        video: {
            width: { ideal: 1920 },
            height: { ideal: 1080 }
        }
    };
    navigator.mediaDevices.getDisplayMedia(constraints).then(stream => {
        currentStream = stream;
        stream.oninactive = uncast;
        connect();
    }).catch(err => { alert(err) });
}

function connect() {
    peer = new Peer();
    peer.on('open', () => {
        socket = io();
        socket.on('projector-ready', id => {
            peer.call(id, currentStream);
        });
        socket.on('projector-stop', function () {
            uncast();
        });
        socket.emit('cast', response => {
            console.log(response);
        });
    });
}

function uncast() {
    if (currentStream != undefined) {
        currentStream.getTracks().forEach(n => { n.stop() });
    }
    if (socket != undefined) socket.disconnect();
    if (peer != undefined) peer.disconnect();
}
