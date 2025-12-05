from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.listing import Listing
from app.models.review import Review


REVIEWS_PATH = "/api/v1/reviews"
BUYER_MY_REVIEWS_PATH = "/api/v1/reviews/my"
ADMIN_REVIEWS_PATH = "/api/v1/admin/reviews"


def _login(client: TestClient, email: str, password: str = "secret") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def test_buyer_reviews_purchased_car_and_admin_sees_review(
    client: TestClient,
    db: Session,
    buyer_user: User,
    admin_user: User,
    sample_listing: Listing,
):
    # 1) Login buyer
    buyer_token = _login(client, buyer_user.email)

    # 3) Buyer crea una review para ese listing
    review_payload = {
        "listing_id": sample_listing.id,
        "rating": 4,
        "comment": "Muy buen auto para ciudad",
    }
    resp_review = client.post(
        REVIEWS_PATH,
        json=review_payload,
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp_review.status_code == status.HTTP_200_OK, resp_review.text
    review_body = resp_review.json()

    assert review_body["rating"] == 4
    assert review_body["comment"] == "Muy buen auto para ciudad"
    assert review_body["author_id"] == buyer_user.id
    # car_model_id debe coincidir con el del listing
    assert review_body["car_model_id"] == sample_listing.car_model_id

    # 4) Verificamos la Review en DB
    review_in_db = (
        db.query(Review)
        .filter(
            Review.id == review_body["id"],
            Review.car_model_id == sample_listing.car_model_id,
            Review.author_id == buyer_user.id,
        )
        .first()
    )
    assert review_in_db is not None

    # 5) Buyer consulta "mis reviews"
    resp_my_reviews = client.get(
        BUYER_MY_REVIEWS_PATH,
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp_my_reviews.status_code == status.HTTP_200_OK, resp_my_reviews.text
    my_reviews = resp_my_reviews.json()

    assert isinstance(my_reviews, list)

    # BuyerReviewOut:
    # id, car_model_id, brand, model, rating, comment, created_at
    buyer_review_entry = next(
        (r for r in my_reviews if r["car_model_id"] == sample_listing.car_model_id),
        None,
    )
    assert (
        buyer_review_entry is not None
    ), "El buyer no ve su propia review en /reviews/my"

    assert buyer_review_entry["brand"] == sample_listing.brand
    assert buyer_review_entry["model"] == sample_listing.model
    assert buyer_review_entry["rating"] == 4
    assert buyer_review_entry["comment"] == "Muy buen auto para ciudad"

    # 6) Login admin
    admin_token = _login(client, admin_user.email)

    # 7) Admin consulta el listado paginado de reviews
    resp_admin_reviews = client.get(
        ADMIN_REVIEWS_PATH,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_admin_reviews.status_code == status.HTTP_200_OK, resp_admin_reviews.text
    admin_reviews_data = resp_admin_reviews.json()

    # PaginatedAdminReviewsOut: { items: [...], total, page, page_size }
    assert "items" in admin_reviews_data
    admin_items = admin_reviews_data["items"]
    assert isinstance(admin_items, list)

    admin_review_entry = next(
        (
            r
            for r in admin_items
            if r["buyer_id"] == buyer_user.id
            and r["brand"] == sample_listing.brand
            and r["model"] == sample_listing.model
        ),
        None,
    )
    assert (
        admin_review_entry is not None
    ), "Admin no ve la review del buyer en /admin/reviews"

    # AdminReviewOut:
    # id, car_model_id, brand, model, buyer_id, buyer_email, rating, comment, created_at
    assert admin_review_entry["buyer_email"] == buyer_user.email
    assert admin_review_entry["rating"] == 4
    assert admin_review_entry["comment"] == "Muy buen auto para ciudad"
