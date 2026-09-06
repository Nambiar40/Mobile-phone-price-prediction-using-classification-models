import requests
from bs4 import BeautifulSoup

url = 'https://www.flipkart.com/realme-gt-7t-icesense-blue-256-gb/p/itmda26d662ee28e?pid=MOBHFQ6DRD7YD3SG&marketplace=FLIPKART&lid=LSTMOBHFQ6DRD7YD3SGXOEXUP&q=realme+gt+7t&fm=organic&pageUID=1788686133996'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
soup = BeautifulSoup(r.content, 'html.parser')
title = soup.find('span', {'class': 'VU-Tz5'}) or soup.find('span', {'class': 'B_NuCI'})
price = soup.find('div', {'class': 'Nx9bqj CxhGGd'}) or soup.find('div', {'class': '_30jeq3 _16Jk6d'})
print("Title:", title.get_text() if title else None)
print("Price:", price.get_text() if price else None)
