from typing import Optional
import uuid
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db

SECRET="w9skXw21" #its a localhost app so secrecy doesn't matter

class UserManager(UUIDIDMixin,BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret=SECRET
    verification_token_secret= SECRET
    async def on_after_forgot_password(self, user, token, request = None):
        return await super().on_after_forgot_password(user, token, request)
    async def on_after_register(self, user, request = None):
        return await super().on_after_register(user, request)
    async def on_after_request_verify(self, user, token, request = None):
        return await super().on_after_request_verify(user, token, request)
    
async def get_user_manager(user_db: SQLAlchemyUserDatabase= Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport=BearerTransport(tokenUrl="auth/jwt/login")
