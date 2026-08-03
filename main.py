from fastapi import FastAPI
from api import auth, users, verification
from typing import Annotated
app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(verification.router)

@app.get("/root")
async def root():
    return {"msg": 'root'}

from fastapi import Cookie

@app.get("/test-cookie")
async def test_cookie(
    refresh_token: Annotated[str | None, Cookie()] = None
):
    return {
        "cookie": refresh_token
    }