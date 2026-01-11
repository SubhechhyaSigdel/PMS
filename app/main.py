from fastapi import FastAPI
from .routes import users,auth,rooms

app=FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(rooms.router)

@app.get("/")
def index():
    return {"Hey":"There"}