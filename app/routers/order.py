from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates  
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.models import Order, OrderStatus
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

templates = Jinja2Templates(directory="templates")


@router.get("/health")
def orders_health_check():
    return {"message": "working"}


@router.get("/")
def all_orders_page(request: Request, db: Session = Depends(get_db)):
    all_orders = db.scalars(select(Order)).all()
    return templates.TemplateResponse(
        request=request,
        name="order.html",
        context={
            "title": "Order",
            "orders": all_orders,
        },
    )