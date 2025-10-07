from typing import Dict
from fastapi import APIRouter, WebSocket

from api.chat.domain.services import ChatServices
from api.chat.application.chat_use_cases import ChatUseCases


class ConnectionManager:
    def __init__(self):
        # company -> username -> WebSocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, company: str, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(company, {})[username] = websocket

    def disconnect(self, company: str, username: str):
        conns = self.active_connections.get(company, {})
        conns.pop(username, None)

    async def send_personal_message(self, company: str, username: str, message: str):
        ws = self.active_connections.get(company, {}).get(username)
        if ws:
            await ws.send_text(message)


chat_router = APIRouter(prefix="/chat-ws", tags=["Chat WebSocket"])


def get_chat_use_cases():
    return ChatUseCases(chat_services=ChatServices())
