from app.db.database import engine, Base
from app.models import user, product

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.schemas.product_schema import ProductCreate
from app.models.product import Product
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.services.amazon_scraper import get_amazon_price



app = FastAPI()

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = User(
            email=user.email,
            password_hash=user.password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User registered successfully"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    price = None

    if "amazon" in product.product_url.lower():
        price = get_amazon_price(product.product_url)

    new_product = Product(
        user_id=product.user_id,
        product_url=product.product_url,
        product_name=product.product_name,
        platform=product.platform
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully",
        "current_price": price
    }
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products
