
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.database import get_db
from app.models.users import User

router = APIRouter(prefix="/users", tags=["users"])

templates = Jinja2Templates(directory="app/templates")

password_hash = PasswordHash.recommended()


@router.get("/health")
def users_health_check():
    return {"message": "working"}



@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None}
    )


@router.post("/register")
def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Пароли не совпадают"},
            status_code=400
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Пароль должен содержать минимум 8 символов"},
            status_code=400
        )

    existing_user = db.scalars(
        select(User).where(
            or_(
                User.email == email,
                User.phone == phone
            )
        )
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Email или телефон уже используется"},
            status_code=400
        )

    new_user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        hashed_password=password_hash.hash(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(
        url="/login",
        status_code=303
    )



@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    email = email.strip().lower()

    user = db.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user or not password_hash.verify(
        password,
        user.hashed_password
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
            status_code=401
        )

    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Аккаунт заблокирован"},
            status_code=403
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/orders/",
        status_code=303
    )



@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
