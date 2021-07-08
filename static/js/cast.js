var socket, peer, stream;

function cast() {
    if (/Mobi/.test(navigator.userAgent)) {
        alert("Proyectar la pantalla no es compatible con dispositivos móviles.\n\nSe recomienda usar un ordenador Windows o Apple con Chrome, Edge o Safari.");
        return;
    }

    _uncast();

    var constraints = {
        audio: false,
        video: {
            width: { ideal: 1920 },
            height: { ideal: 1080 }
        }
    };

    navigator.mediaDevices.getDisplayMedia(constraints).then(screen => {
        stream = screen;
        stream.oninactive = _uncast;
        _cast();
    }).catch(err => { alert(err) });
}

function _cast() {
    socket = io();

    socket.on('connect', () => {
        socket.emit('cast');
    });

    peer = new SimplePeer({
        stream: stream,
        config: {
            iceServers: [{
                urls: 'turn:' + location.hostname,
                username: "winvideo",
                credential: "looper"
            }]
        }
    });

    peer.on('error', err => {
        alert(err);
        _uncast();
        _cast();
    });

    peer.on('signal', signal => {
        socket.emit('signal', signal)
    });

    socket.on('signal', (data) => {
        peer.signal(data);
    });

    socket.on('stop', () => {
        _uncast();
    });
}

function _uncast() {
    if (stream != undefined) {
        stream.getTracks().forEach(n => { n.stop() });
    }
    if (peer != undefined) peer.destroy();
    if (socket != undefined) socket.disconnect();
}