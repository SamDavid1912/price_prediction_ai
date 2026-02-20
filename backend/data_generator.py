import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.product import Product
from app.models.product_platform import ProductPlatform
from app.models.price_history import PriceHistory


PLATFORMS = ["Amazon", "Flipkart", "Myntra"]

# ------------------- SMARTPHONES ------------------- #

SMARTPHONES = {
    # iPhone 17 Series
    "iPhone 17": ["128GB", "256GB"],
    "iPhone 17 Plus": ["128GB", "256GB"],
    "iPhone 17 Pro": ["256GB", "512GB"],
    "iPhone 17 Pro Max": ["256GB", "512GB", "1TB"],

    # iPhone 16 Series
    "iPhone 16": ["128GB", "256GB"],
    "iPhone 16 Plus": ["128GB", "256GB"],
    "iPhone 16 Pro": ["256GB", "512GB"],
    "iPhone 16 Pro Max": ["256GB", "512GB", "1TB"],

    # iPhone 15 Series
    "iPhone 15": ["128GB", "256GB"],
    "iPhone 15 Plus": ["128GB", "256GB"],
    "iPhone 15 Pro": ["256GB", "512GB"],
    "iPhone 15 Pro Max": ["256GB", "512GB", "1TB"],

    # Samsung
    "Samsung Galaxy S24": ["128GB", "256GB"],
    "Samsung Galaxy S24+": ["256GB", "512GB"],
    "Samsung Galaxy S24 Ultra": ["256GB", "512GB", "1TB"],

    # Others
    "OnePlus 12": ["256GB", "512GB"],
    "Google Pixel 8": ["128GB", "256GB"],
    "Nothing Phone 2": ["128GB", "256GB"],
    "Xiaomi 14": ["256GB", "512GB"],
    "iQOO 12": ["256GB", "512GB"],
}

# ------------------- LAPTOPS ------------------- #

LAPTOPS = {
    "MacBook Air M3": ["8GB/256GB", "8GB/512GB", "16GB/512GB"],
    "MacBook Pro 14 M3": ["16GB/512GB", "16GB/1TB"],
    "Dell XPS 13 Plus": ["16GB/512GB"],
    "HP Spectre x360": ["16GB/1TB"],
    "Lenovo ThinkPad X1 Carbon": ["16GB/1TB"],
    "ASUS ROG Zephyrus G14": ["16GB/1TB"],
}

# ------------------- TVs ------------------- #

TVS = {
    "LG OLED C3": ["55-inch", "65-inch"],
    "Samsung QLED Q80C": ["55-inch", "65-inch"],
    "Sony Bravia X90L": ["55-inch", "65-inch"],
    "OnePlus Q2 Pro": ["55-inch", "65-inch"],
    "Mi X Series 4K": ["50-inch", "55-inch"],
}

# ------------------- AUDIO ------------------- #

AUDIO = {
    "Sony WH-1000XM5": ["Black", "Silver"],
    "Bose QuietComfort Ultra": ["Black", "White"],
    "AirPods Pro 2": ["Standard"],
    "JBL Flip 6": ["Black", "Blue"],
    "Boat Rockerz 550": ["Black", "Red"],
    "Samsung Galaxy Buds 2 Pro": ["Black", "White"],
}

# ------------------- FASHION ------------------- #

FASHION = {
    "Nike Air Max 270": ["UK 7", "UK 8", "UK 9"],
    "Adidas Ultraboost 23": ["UK 7", "UK 8", "UK 9"],
    "Puma RS-X": ["UK 7", "UK 8"],
    "Levi's 511 Jeans": ["32", "34", "36"],
    "Allen Solly Formal Shirt": ["M", "L", "XL"],
    "H&M Hoodie": ["M", "L", "XL"],
}

# ------------------- BEAUTY ------------------- #

BEAUTY = {
    "Bare Anatomy Shampoo": ["250ml", "500ml"],
    "Mamaearth Face Wash": ["100ml"],
    "Dove Body Wash": ["250ml", "500ml"],
    "L'Oreal Hyaluronic Serum": ["50ml"],
    "Minimalist Sunscreen SPF50": ["50g"],
    "Plum Green Tea Toner": ["200ml"],
}

# ------------------- HOME APPLIANCES ------------------- #

HOME_APPLIANCES = {
    "Dyson V15 Detect": ["Standard"],
    "Philips Air Fryer XXL": ["6.2L"],
    "LG Front Load Washing Machine": ["7kg", "8kg"],
    "Samsung Double Door Refrigerator": ["253L", "345L"],
    "IFB Convection Microwave Oven": ["23L", "30L"],
    "Kent Supreme RO Water Purifier": ["Standard"],
}

CATEGORIES = {
    "Electronics": [SMARTPHONES, LAPTOPS, TVS, AUDIO],
    "Fashion": [FASHION],
    "Beauty": [BEAUTY],
    "Home Appliances": [HOME_APPLIANCES],
}


def generate_product():
    category = random.choice(list(CATEGORIES.keys()))
    family_group = random.choice(CATEGORIES[category])
    base_model = random.choice(list(family_group.keys()))
    variant = random.choice(family_group[base_model])
    return f"{base_model} {variant}", category


def run():
    print("Generating latest realistic Indian-market dataset...")
    db: Session = SessionLocal()

    for i in range(1000):

        name, category = generate_product()

        product = Product(
            name=name,
            category=category,
            brand=name.split()[0]
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        base_price = random.randint(8000, 150000)

        for platform in PLATFORMS:

            platform_entry = ProductPlatform(
                product_id=product.id,
                platform=platform,
                product_url=f"https://{platform.lower()}.com/{product.id}"
            )

            db.add(platform_entry)
            db.commit()
            db.refresh(platform_entry)

            current_price = base_price + random.randint(-3000, 3000)

            for day in range(60):
                date = datetime.today() - timedelta(days=day)
                fluctuation = random.uniform(-0.02, 0.02)
                current_price *= (1 + fluctuation)

                price_entry = PriceHistory(
                    product_platform_id=platform_entry.id,
                    price=round(current_price, 2),
                    availability=True,
                    seller=platform,
                    recorded_at=date
                )

                db.add(price_entry)

            db.commit()

        if i % 100 == 0:
            print(f"{i} products created...")

    db.close()
    print("Latest realistic dataset generation completed!")


if __name__ == "__main__":
    run()