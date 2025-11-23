from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.listing import Listing
from app.schemas.review import ReviewCreate, ReviewOut
from app.services import reviews as reviews_service

router = APIRouter()


@router.post(
    "",
    response_model=ReviewOut,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una review para el CarModel asociado a la listing indicada.
    """
    return reviews_service.create_review_for_buyer(
        db=db,
        buyer=current_user,
        payload=payload,
    )


@router.get(
    "/by-listing/{listing_id}",
    response_model=list[ReviewOut],
)
def list_reviews_by_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    """
    Lista las reviews del CarModel asociado a la listing dada.
    (sin exigir estar logueado, modo lectura pública)
    """
    listing = db.get(Listing, listing_id)
    if not listing:
        return []

    return reviews_service.list_reviews_for_listing(
        db=db,
        listing=listing,
    )
