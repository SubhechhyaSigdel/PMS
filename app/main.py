from fastapi import FastAPI
from .routes import users,auth,rooms,reservations,guest

app=FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(guest.router)
app.include_router(reservations.router)

@app.get("/")
def index():
    return {"Happy":"Moments"}