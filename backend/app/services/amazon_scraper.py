import requests
from bs4 import BeautifulSoup


def get_amazon_price(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    price = None

    # Amazon price id usually:
    price_tag = soup.find("span", {"class": "a-price-whole"})

    if price_tag:
        price = price_tag.text.strip()

    return price
