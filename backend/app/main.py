from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import engine, Base, get_db

from app.models.user import User
from app.models.product import Product
from app.models.product_platform import ProductPlatform
from app.models.price_history import PriceHistory
from app.models.price_prediction import PricePrediction
from app.models.festival import Festival
from datetime import datetime, timedelta
from app.schemas.user_schema import UserCreate
from app.schemas.product_schema import ProductCreate, ProductResponse
from app.schemas.product_platform_schema import ProductPlatformCreate, ProductPlatformResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()


# -------------------- USER REGISTER --------------------

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        email=user.email,
        password_hash=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# -------------------- CREATE PRODUCT --------------------

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    new_product = Product(
        name=product.name,
        category=product.category,
        brand=product.brand
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# -------------------- GET ALL PRODUCTS --------------------

@app.get("/products")
def get_products(
    page: int = 1,
    limit: int = 20,
    category: str = None,
    db: Session = Depends(get_db)
):

    offset = (page - 1) * limit

    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    products = query.offset(offset).limit(limit).all()

    return products


# -------------------- ADD PLATFORM --------------------

@app.post("/product-platforms", response_model=ProductPlatformResponse)
def add_platform(platform: ProductPlatformCreate, db: Session = Depends(get_db)):

    new_platform = ProductPlatform(
        product_id=platform.product_id,
        platform=platform.platform,
        product_url=platform.product_url
    )

    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)

    return new_platform


# -------------------- COMPARE PRICES --------------------

@app.get("/products/{product_id}/compare")
def compare_prices(product_id: int, db: Session = Depends(get_db)):

    result = []

    platforms = db.query(ProductPlatform).filter(
        ProductPlatform.product_id == product_id
    ).all()

    for platform in platforms:
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_platform_id == platform.id)
            .order_by(PriceHistory.recorded_at.desc())
            .first()
        )

        if latest_price:
            result.append({
                "platform": platform.platform,
                "latest_price": float(latest_price.price),
                "recorded_at": latest_price.recorded_at
            })

    return result
@app.get("/products/{product_id}/predict")
def predict_price(product_id: int, db: Session = Depends(get_db)):

    result = []

    today = datetime.today().date()
    next_month = today + timedelta(days=30)

    upcoming_festival = (
        db.query(Festival)
        .filter(Festival.festival_date.between(today, next_month))
        .first()
    )

    platforms = db.query(ProductPlatform).filter(
        ProductPlatform.product_id == product_id
    ).all()

    for platform in platforms:
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_platform_id == platform.id)
            .order_by(PriceHistory.recorded_at.desc())
            .first()
        )

        if not latest_price:
            continue



        # ---------------- TREND + FESTIVAL BASED PREDICTION ----------------
        current_price = float(latest_price.price)
        # Get last 3 price entries
        last_prices = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_platform_id == platform.id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(3)
            .all()
        )

        if len(last_prices) >= 2:
            trend_drop = float(last_prices[0].price) - float(last_prices[-1].price)
        else:
            trend_drop = 0

        # Basic trend projection
        predicted_price = current_price - (trend_drop / 2)

        # Festival impact
        if upcoming_festival:
            if upcoming_festival.expected_discount_level == "High":
                predicted_price *= 0.9
            elif upcoming_festival.expected_discount_level == "Medium":
                predicted_price *= 0.95

        # Final suggestion logic
        if predicted_price < current_price:
            suggestion = "Wait for Better Price"
        else:
            suggestion = "Buy Now"

        
        # ---------------- CONFIDENCE SCORE LOGIC ----------------

        total_records = db.query(PriceHistory).filter(
            PriceHistory.product_platform_id == platform.id
        ).count()

        if total_records >= 20:
            base_confidence = 85
        elif total_records >= 10:
            base_confidence = 75
        else:
            base_confidence = 60

        # Trend stability check
        if len(last_prices) >= 2:
            variation = abs(float(last_prices[0].price) - float(last_prices[1].price))
            if variation < 5:
                base_confidence += 5
            elif variation > 20:
                base_confidence -= 10

        # Festival influence
        if upcoming_festival:
            base_confidence += 5

        confidence_score = min(base_confidence, 95)
        # ---------------- EXPLANATION ENGINE ----------------

        price_difference = round(current_price - predicted_price, 2)

        if upcoming_festival:
            explanation = (
                f"Price has been trending downward and {upcoming_festival.name} "
                f"is approaching. A potential drop of ₹{price_difference} is expected."
            )
        else:
            explanation = (
                f"Recent trend shows limited change. Expected variation is ₹{price_difference}."
            )

        new_prediction = PricePrediction(
            product_platform_id=platform.id,
            predicted_price=round(predicted_price, 2),
            predicted_drop=round(current_price - predicted_price, 2),
            best_buy_time=upcoming_festival.festival_date if upcoming_festival else None,
            confidence_score=confidence_score
        )   

        db.add(new_prediction)
        db.commit()

            # ---- existing result append ----
        result.append({
            "platform": platform.platform,
            "current_price": current_price,
            "predicted_price_next_month": round(predicted_price, 2),
            "festival": upcoming_festival.name if upcoming_festival else None,
            "suggestion": suggestion,
            "explanation": explanation
        })
    return result