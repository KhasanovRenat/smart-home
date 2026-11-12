import os
from datetime import datetime, timedelta, timezone
from secrets import compare_digest

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.environ["APP_PASSWORD"]
JWT_SECRET = os.environ["JWT_SECRET"]
if len(JWT_SECRET.encode()) < 32:
    raise ValueError("JWT_SECRET must contain at least 32 bytes")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def invalid_credentials():
    return HTTPException(401, "Неверные данные для входа или токен", headers={"WWW-Authenticate": "Bearer"})


def issue_token(form: OAuth2PasswordRequestForm = Depends()):
    username_matches = compare_digest(form.username.encode(), APP_USERNAME.encode())
    password_matches = compare_digest(form.password.encode(), APP_PASSWORD.encode())
    if not (username_matches and password_matches):
        raise invalid_credentials()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode({"sub": APP_USERNAME, "exp": expiration}, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"require": ["exp", "sub"]})
    except jwt.InvalidTokenError as error:
        raise invalid_credentials() from error
    if payload["sub"] != APP_USERNAME:
        raise invalid_credentials()
    return payload["sub"]
