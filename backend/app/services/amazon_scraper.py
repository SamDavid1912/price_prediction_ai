import requests
from bs4 import BeautifulSoup


def get_amazon_price(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Request failed:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    whole = soup.find("span", {"class": "a-price-whole"})
    fraction = soup.find("span", {"class": "a-price-fraction"})

    if whole and fraction:
        price_str = whole.text.replace(",", "").strip() + "." + fraction.text.strip()
        return float(price_str)

    print("Price not found in HTML")
    return None