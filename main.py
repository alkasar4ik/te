
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.database import init_db
from app.routers import orders, user


init_db()

app = FastAPI(
    title="ServiceDesk Plus",
    description="Система керування заявками",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key="my-secret-key-for-servicedesk-project"
)

app.include_router(orders.router)
app.include_router(user.router)


@app.get("/")
def home():
    return RedirectResponse(
        url="/orders/",
        status_code=303
    )


@app.get("/health_check")
def main_health_check():
    return {"message": "working"}
