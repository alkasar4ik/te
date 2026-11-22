
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tickets import Order

router = APIRouter(prefix="/orders", tags=["orders"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def list_pending_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == "pending").all()

    return templates.TemplateResponse(
        request=request,
        name="all_orders.html",
        context={"orders": orders}
    )


@router.get("/create")
def create_order_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="orders_create.html",
        context={}
    )


@router.post("/create")
def create_order(
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    new_order = Order(
        title=title,
        description=description,
        status="pending"
    )

    db.add(new_order)
    db.commit()

    return RedirectResponse(
        url="/orders/",
        status_code=303
    )


@router.get("/accepted")
def list_accepted_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == "accepted").all()

    return templates.TemplateResponse(
        request=request,
        name="all_orders.html",
        context={"orders": orders}
    )


@router.get("/{order_id}")
def detail_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return templates.TemplateResponse(
        request=request,
        name="detail_orders.html",
        context={"order": order}
    )


@router.post("/{order_id}/accept")
def accept_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "accepted"
    db.commit()

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )


@router.post("/{order_id}/close")
def close_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "closed"
    db.commit()

    return RedirectResponse(
        url=f"/orders/{order_id}",
        status_code=303
    )
