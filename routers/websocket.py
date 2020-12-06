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
        await run_until_first_complete(
            (self.chatroom_ws_receiver, {"websocket": websocket}),
            (self.chatroom_ws_sender, {"websocket": websocket}),
        )

    async def chatroom_ws_receiver(self, websocket):
        async for message in websocket.iter_text():
            await broadcast.publish(channel="chatroom", message=message)

    async def chatroom_ws_sender(self, websocket):
        async with broadcast.subscribe(channel="chatroom") as subscriber:
            async for event in subscriber:
                await websocket.send_text(event.message)


routes = [WebSocketRoute('/chat', Chat)]
router = APIRouter(routes,
                   on_startup=[broadcast.connect],
                   on_shutdown=[broadcast.disconnect])
