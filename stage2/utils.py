import requests, random, datetime
from PIL import Image, ImageDraw, ImageFont

COUNTRIES_API = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
EXCHANGE_API = "https://open.er-api.com/v6/latest/USD"

def fetch_countries():
    r = requests.get(COUNTRIES_API, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_exchange_rates():
    r = requests.get(EXCHANGE_API, timeout=10)
    r.raise_for_status()
    return r.json()["rates"]

def compute_estimated_gdp(population, exchange_rate):
    if not exchange_rate or exchange_rate == 0:
        return 0
    # Generate fresh random multiplier (1000-2000) for each call
    multiplier = random.randint(1000, 2000)
    return (population * multiplier) / exchange_rate

def generate_summary_image(top5, total, timestamp):
    img = Image.new('RGB', (600, 400), color=(230, 230, 250))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((20, 20), f"Total Countries: {total}", fill="black", font=font)
    draw.text((20, 50), f"Last Refreshed: {timestamp}", fill="black", font=font)
    draw.text((20, 90), "Top 5 Countries by GDP:", fill="black", font=font)

    y = 120
    for c in top5:
        draw.text((40, y), f"{c[0]} - GDP: {c[1]:,.2f}", fill="black", font=font)
        y += 25

    img.save("cache_summary.png")
