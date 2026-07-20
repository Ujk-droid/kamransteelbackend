from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.client_project import ClientProject
from app.models.estimate import Estimate
from app.models.product import Product

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[str], dependencies=[Depends(get_current_admin)])
def list_categories(session: Session = Depends(get_session)):
    product_categories = session.exec(select(Product.category).distinct()).all()
    estimate_categories = session.exec(select(Estimate.category).distinct()).all()
    client_project_categories = session.exec(
        select(ClientProject.category).distinct()
    ).all()
    return sorted(
        set(product_categories) | set(estimate_categories) | set(client_project_categories)
    )
