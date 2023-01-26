from fastapi import FastAPI
from oauth_middleware import LoginMiddleware

app = FastAPI()
app.add_middleware(LoginMiddleware, users={}, admin_scope="jesus")


@app.get("/")
async def root():
    return {"message": "Hello World"}
