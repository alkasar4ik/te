
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tickets import Order, OrderStatus, OrderPriority
from app.models.users import User, UserRole

router = APIRouter(prefix="/orders", tags=["orders"])

templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        request.session.clear()
        return None

    return user


def check_staff(user: User):
    if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="У вас немає доступу"
        )


@router.get("/")
def list_pending_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    query = db.query(Order).filter(
        Order.status == OrderStatus.PENDING
    )

    if user.role == UserRole.CLIENT:
        query = query.filter(Order.client_id == user.id)

    orders = query.all()

    return templates.TemplateResponse(
        request=request,
        name="all_orders.html",
        context={
            "orders": orders,
            "current_user": user
        }
    )


@router.get("/create")
def create_order_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    if user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=403,
            detail="Створювати заявки можуть тільки клієнти"
        )

    return templates.TemplateResponse(
        request=request,
        name="orders_create.html",
        context={"current_user": user}
    )


@router.post("/create")
def create_order(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    if user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=403,
            detail="Створювати заявки можуть тільки клієнти"
        )

    new_order = Order(
        title=title,
        description=description,
        status=OrderStatus.PENDING,
        priority=OrderPriority.MEDIUM,
        client_id=user.id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return RedirectResponse(
        url="/orders/",
        status_code=303
    )


@router.get("/accepted")
def list_accepted_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    check_staff(user)

    orders = db.query(Order).filter(
        Order.status == OrderStatus.ACCEPTED
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="all_orders.html",
        context={
            "orders": orders,
            "current_user": user
        }
    )


@router.get("/{order_id}")
def detail_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заявку не знайдено"
        )

    if user.role == UserRole.CLIENT and order.client_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Це не ваша заявка"
        )

    return templates.TemplateResponse(
        request=request,
        name="detail_orders.html",
        context={
            "order": order,
            "current_user": user
        }
    )


@router.post("/{order_id}/accept")
def accept_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    check_staff(user)

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заявку не знайдено"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Цю заявку вже опрацьовано"
        )

    order.status = OrderStatus.ACCEPTED
    order.master_id = user.id

    db.commit()

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )


@router.post("/{order_id}/reject")
def reject_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    check_staff(user)

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заявку не знайдено"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Цю заявку вже опрацьовано"
        )

    order.status = OrderStatus.REJECTED

    db.commit()

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )


@router.post("/{order_id}/close")
def close_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(
            url="/users/login",
            status_code=303
        )

    check_staff(user)

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Заявку не знайдено"
        )

    if order.status != OrderStatus.ACCEPTED:
        raise HTTPException(
            status_code=400,
            detail="Закрити можна тільки прийняту заявку"
        )

    order.status = OrderStatus.CLOSED

    db.commit()

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )
