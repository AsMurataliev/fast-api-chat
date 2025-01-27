from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    id: UUID4
    login: str
    nick_name: str
    group: str
    password: str
    chat_ids: List[UUID4] = []

class Message(BaseModel):
    id: UUID4
    text: str
    user_id: UUID4
    date_time: datetime

class Chat(BaseModel):
    id: UUID4
    name: str
    user_ids: List[UUID4]
    message_ids: List[UUID4] = []

class CreateMessageDTO(BaseModel):
    text: str
    user_id: UUID4
    chat_id: UUID4

class CreateChatDTO(BaseModel):
    name: str
    user_ids: List[UUID4]

class RegisterUserDTO(BaseModel):
    login: str
    password: str
    nick_name: str
    group: str

class LoginUserDTO(BaseModel):
    login: str
    password: str

class ReadMessageDTO(BaseModel):
    id: UUID4
    text: str
    user_id: UUID4
    date_time: datetime

class ReadChatDTO(BaseModel):
    id: UUID4
    name: str
    user_ids: List[UUID4]
    messages: List[ReadMessageDTO]

class ReadUserForChatDTO(BaseModel):
    id: UUID4
    nick_name: str

class ReadLinkChatDTO(BaseModel):
    id: UUID4
    name: str

class GetAccountOfUserDTO(BaseModel):
    login: str
    nick_name: str
    group: str
    chats: List[ReadLinkChatDTO]


app = FastAPI()

users = {}
chats = {}
messages = {}




@app.post("/register/", response_model=User)
async def register_user(user: RegisterUserDTO):
    user_id = uuid4()
    new_user = User(
        id=user_id,
        login=user.login,
        nick_name=user.nick_name,
        group=user.group,
        password=user.password,
        chat_ids=[]
    )
    users[user_id] = new_user
    return new_user

@app.post("/login/", response_model=GetAccountOfUserDTO)
async def login_user(credentials: LoginUserDTO):
    for user_id, user in users.items():
        if user.login == credentials.login and user.password == credentials.password:
            user_chats = [ReadLinkChatDTO(id=chat_id, name=chats[chat_id].name) for chat_id in user.chat_ids if chat_id in chats]
            return GetAccountOfUserDTO(
                login=user.login,
                nick_name=user.nick_name,
                group=user.group,
                chats=user_chats
            )
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/chats/", response_model=Chat)
async def create_chat(chat: CreateChatDTO):
    chat_id = uuid4()
    new_chat = Chat(
        id=chat_id,
        name=chat.name,
        user_ids=chat.user_ids,
        message_ids=[]
    )
    chats[chat_id] = new_chat
    for user_id in chat.user_ids:
        if user_id in users:
            users[user_id].chat_ids.append(chat_id)
    return new_chat

@app.post("/messages/", response_model=Message)
async def create_message(message: CreateMessageDTO):
    message_id = uuid4()
    new_message = Message(
        id=message_id,
        text=message.text,
        user_id=message.user_id,
        date_time=datetime.now()
    )
    messages[message_id] = new_message
    if message.chat_id in chats:
        chats[message.chat_id].message_ids.append(message_id)
    return new_message

@app.get("/chats/{chat_id}", response_model=ReadChatDTO)
async def get_chat(chat_id: UUID4):
    if chat_id in chats:
        chat = chats[chat_id]
        chat_messages = [messages[msg_id] for msg_id in chat.message_ids if msg_id in messages]
        return ReadChatDTO(
            id=chat.id,
            name=chat.name,
            user_ids=chat.user_ids,
            messages=chat_messages
        )
    raise HTTPException(status_code=404, detail="Chat not found")

@app.get("/users/{user_id}", response_model=GetAccountOfUserDTO)
async def get_user(user_id: UUID4):
    if user_id in users:
        user = users[user_id]
        user_chats = [ReadLinkChatDTO(id=chat_id, name=chats[chat_id].name) for chat_id in user.chat_ids if chat_id in chats]
        return GetAccountOfUserDTO(
            login=user.login,
            nick_name=user.nick_name,
            group=user.group,
            chats=user_chats
        )
    raise HTTPException(status_code=404, detail="User not found")
