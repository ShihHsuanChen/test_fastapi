from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <div id='timer'></div>
        <div>
            <button id=connectButton onclick=connectHandler(event)>Connect</button>
            <span id='status'><- Click to connect</span>
        </div>
        <div>
            <button id=taskButton onclick=taskHandler(event)>Run A Task</button>
            <button id=taskButton2 onclick=taskHandler2(event)>Run A Task2</button>
        </div>
        <div>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'></ul>
        </div>
        <div>
            <h2>Your ID: <span id="ws-id"></span></h2>
            <form action="" onsubmit="sendMessage2(event)">
                <input type="text" id="messageText2" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages2'></ul>
        </div>
        <script>
            var ws = new WebSocket("ws://10.0.4.53:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }

            var ws2 = new WebSocket("ws://10.0.4.53:8000/ws2");
            ws2.onmessage = function(event) {
                var messages = document.getElementById('timer');
                messages.innerHTML = event.data;
            };

            function connectHandler(event) {
                var but = document.getElementById('connectButton');
                if (but.innerHTML == 'Connect') {
                    ws3 = new WebSocket("ws://10.0.4.53:8000/ws3");
                    ws3.onmessage = function(event) {
                        var messages = document.getElementById('status');
                        messages.innerHTML = event.data;
                    };
                    but.innerHTML = 'Disconnect';
                } else {
                    if (ws3 !== null) ws3.close();
                    but.innerHTML = 'Connect';
                    var statusDom = document.getElementById('status');
                    statusDom.innerHTML = 'Connection closed'
                }
            }
            var ws3 = null;

            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws4 = new WebSocket(`ws://10.0.4.53:8000/ws4/${client_id}`);
            ws4.onmessage = function(event) {
                var messages = document.getElementById('messages2')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage2(event) {
                console.log(event)
                var input = document.getElementById("messageText2")
                ws4.send(input.value)
                input.value = ''
                event.preventDefault()
            }
            function taskHandler(event) {
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open("GET", '/run_task', true); // false for synchronous request
                xmlHttp.send();
                console.log('send task')
            }
            function taskHandler2(event) {
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open("GET", '/run_task2', true); // false for synchronous request
                xmlHttp.send();
                console.log('send task2')
            }
        </script>
    </body>
</html>
"""

from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

@app.get("/")
async def get():
    return HTMLResponse(html)


# test simple message with while loop
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
        except (WebSocketDisconnect, ConnectionClosedOK):
            print('ws Disconnected!')
            break

import time
import asyncio
from datetime import datetime


# test simple timer with event loop
@app.websocket("/ws2")
async def websocket_endpoint2(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            now = datetime.now()
            msg = f'Now: {now}'
            await websocket.send_text(msg)
            await asyncio.sleep(1)
        except (WebSocketDisconnect, ConnectionClosedOK):
            print('ws2 Disconnected!')
            break


# test connect / disconnect
@app.websocket("/ws3")
async def websocket_endpoint3(websocket: WebSocket):
    st = time.time()
    await websocket.accept()
    while True:
        try:
            msg = f'Connected: {time.time() - st} seconds'
            await websocket.send_text(msg)
            await asyncio.sleep(1)
        except (WebSocketDisconnect, ConnectionClosedOK, ConnectionClosedError):
            print('ws3 Disconnected!')
            break


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = dict()

    async def connect(self, websocket: WebSocket, client_id):
        if client_id in self.active_connections:
            await self.disconnect(client_id)
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, client_id_from):
        for client_id, connection in self.active_connections.items():
            if client_id != client_id_from:
                await connection.send_text(message)


manager = ConnectionManager()


# test multiple clients
@app.websocket("/ws4/{client_id}")
async def websocket_endpoint4(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"Client #{client_id} join the chat", client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat", client_id)


from random import random


async def my_callback(msg):
    await manager.broadcast(msg, 'system')


@app.get('/run_task')
async def run_task():
    current_task_id = task_manager['current_id']
    task_manager['current_id'] += 1
    print('accept', current_task_id)
    await random_loop(my_callback, current_task_id)


@app.get('/run_task2')
def run_task2():
    current_task_id = task_manager['current_id']
    task_manager['current_id'] += 1
    N = 10
    print('test', current_task_id)
    for i in range(N):
        print(f'task {current_task_id} is running [{i+1}/{N}]: {time.time()}')
        time.sleep(1+random()-0.5)


async def random_loop(callback, task_id=None):
    N = 10
    for i in range(N):
        print(f'task {task_id} is running [{i+1}/{N}]: {time.time()}')
        await asyncio.sleep(1+random()-0.5)
        await callback(f'task {task_id} is running [{i+1}/{N}]: {time.time()}')


task_manager = {'current_id': 0}
