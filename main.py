
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.database import init_db
from app.routers import order, user

init_db()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="my-secret-key-for-servicedesk-project"
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(order.router)
app.include_router(user.router)


@app.get("/")
def home():
    return RedirectResponse(url="/orders/", status_code=303)


@app.get("/health_check")
def main_health_check():
    return {"message": "working"}


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )


@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={},
    )
