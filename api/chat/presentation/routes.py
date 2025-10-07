from fastapi import WebSocket, WebSocketDisconnect, Depends
from api.chat.presentation.config import (
    ConnectionManager,
    chat_router,
    ChatUseCases,
    get_chat_use_cases,
)


class ChatWebSocketRoute:
    def __init__(self, prefix: str = "/ws"):
        self.router = chat_router
        self.manager = ConnectionManager()
        self.router.websocket(f"{prefix}/{{company}}/{{username}}")(self.endpoint)

    async def endpoint(
        self,
        websocket: WebSocket,
        company: str,
        username: str,
        use_cases: ChatUseCases = Depends(get_chat_use_cases),
    ):
        await self.manager.connect(company, username, websocket)
        await websocket.send_text(f"Connected as '{username}' in '{company}'.")
        use_cases.verify(company=company, user=username)
        try:
            while True:
                user_msg = await websocket.receive_text()
                reply = use_cases.chat_pipeline(
                    company_id=company, user_id=username, prompt=user_msg
                )
                await self.manager.send_personal_message(company, username, reply)
        except WebSocketDisconnect:
            self.manager.disconnect(company, username)
            print(f"Disconnected '{username}' from '{company}'.")
