import hashlib
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User  # переконайся, що User є в app/models

router = APIRouter(prefix="/users", tags=["users"])

templates = Jinja2Templates(directory="templates")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.get("/health")
def users_health_check():
    return {"message": "working"}


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "title": "Register",
            "error": None,
        },
    )


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    email = email.strip().lower()

    existing_user = db.scalars(
        select(User).where((User.username == username) | (User.email == email))
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "title": "Register",
                "error": "Користувач з таким логіном або email уже існує",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Login",
            "error": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    login_value = login.strip()
    password_hash = hash_password(password)

    user = db.scalars(
        select(User).where(
            ((User.username == login_value) | (User.email == login_value.lower()))
            & (User.hashed_password == password_hash)
        )
    ).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "title": "Login",
                "error": "Невірний логін/email або пароль",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(url="/orders/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/users/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response