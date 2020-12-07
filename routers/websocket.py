from starlette.concurrency import run_until_first_complete
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute
from fastapi import APIRouter
from broadcaster import Broadcast
from starlette.websockets import WebSocket


broadcast = Broadcast('memory://')


class Chat(WebSocketEndpoint):

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        if int(self.scope['path_params']['id']) == 1:
            await run_until_first_complete(
                (self.receive_, {"websocket": websocket}),
                (self.send_, {"websocket": websocket}),
            )
        else:
            await run_until_first_complete(
                (self.receive_, {"websocket": websocket}),
                (self.test, {"websocket": websocket}),
            )

    async def receive_(self, websocket):
        if int(self.scope['path_params']['id']) == 1:
            c = 'chatroom'
        else:
            c = 'puk'
        async for message in websocket.iter_text():
            await broadcast.publish(channel=c, message=message)

    async def send_(self, websocket):
        async with broadcast.subscribe(channel="chatroom") as subscriber:
            async for event in subscriber:
                await websocket.send_text(event.message)

    async def test(self, websocket):
        sub = await broadcast.group_subscribe(['chatroom', 'g1', 'g2'])
        async for event in sub:
            print(self.scope['path_params']['id'])
            await websocket.send_text(event.message)


routes = [WebSocketRoute('/chat/{id}', Chat)]
router = APIRouter(routes,
                   on_startup=[broadcast.connect],
                   on_shutdown=[broadcast.disconnect])
