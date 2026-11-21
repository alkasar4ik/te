from fastapi import FastAPI, Depends, Request, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routers import order, user

app = FastAPI()

app.include_router(order.router)
app.include_router(user.router)

@app.get("/health_check")
def main_health_check():
    return {"message": "working"}