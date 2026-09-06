from app import scrape_flipkart_price

url = "https://www.flipkart.com/realme-gt-7t-icesense-blue-256-gb/p/itmda26d662ee28e?pid=MOBHFQ6DRD7YD3SG"
title, price, img = scrape_flipkart_price(url)
print(f"Title: {title}")
print(f"Price: {price}")
print(f"Image: {img}")
