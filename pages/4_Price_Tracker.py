import streamlit as st
import requests
from bs4 import BeautifulSoup
from db_utils import get_unread_notifications, mark_notifications_read, add_tracked_item, get_tracked_items, delete_tracked_item, update_tracked_price, insert_notification

st.set_page_config(page_title="Price Tracker", page_icon="📈", layout="wide")

st.title("📈 Price Tracker")
st.markdown("Track Amazon product prices and get notified when they drop.")

def scrape_amazon_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, None, None
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find(id='productTitle')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"
        price_tag = soup.find('span', {'class': 'a-price-whole'})
        if not price_tag:
            price_tag = soup.find('span', {'id': 'priceblock_ourprice'})
        price = None
        if price_tag:
            price_str = price_tag.get_text(strip=True).replace(',', '').replace('₹', '').replace('.', '')
            try:
                price = float(price_str)
            except ValueError:
                pass
        img_tag = soup.find(id='landingImage')
        img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""
        return title, price, img_url
    except Exception as e:
        print(f"Scrape error: {e}")
        return None, None, None

# Fetch notifications
try:
    notifications = get_unread_notifications()
    if notifications:
        st.subheader("🔔 Recent Notifications")
        for n in notifications:
            icon = "🎯" if n["type"] == "success" else "🔔"
            st.info(f"{icon} **{n['message']}** ({n['created_at']})")
        
        if st.button("Mark All as Read"):
            ids = [n["id"] for n in notifications]
            mark_notifications_read(ids)
            st.rerun()
except Exception as e:
    st.error(f"Error fetching notifications: {e}")

st.markdown("---")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.subheader("Add New Product to Track")
with col_b:
    if st.button("🔄 Refresh All Prices", use_container_width=True):
        with st.spinner("Checking all tracked items..."):
            items = get_tracked_items()
            updated_count = 0
            for item in items:
                title, new_price, _ = scrape_amazon_price(item['url'])
                if new_price is not None:
                    update_tracked_price(item['id'], new_price)
                    old_price = item.get('current_price')
                    target_price = item.get('target_price')
                    if old_price is None or new_price < old_price:
                        if target_price and new_price <= target_price:
                            insert_notification(f"TARGET REACHED: {item['name']} dropped to ₹{new_price} (Target: ₹{target_price})", 'success')
                        else:
                            insert_notification(f"PRICE DROP: {item['name']} is now ₹{new_price} (was ₹{old_price})", 'info')
                    updated_count += 1
            st.success(f"Successfully refreshed {updated_count} items!")
            st.rerun()

with st.form("add_tracker_form"):
    url = st.text_input("Amazon Product URL *", placeholder="https://www.amazon.in/dp/B0B...")
    target_price = st.number_input("Target Price (₹) - Optional", min_value=0, value=0)
    
    submit = st.form_submit_button("Start Tracking")

if submit:
    url_lower = url.lower()
    if not url or ('amazon' not in url_lower and 'amzn.in' not in url_lower and 'amzn.to' not in url_lower):
        st.error("Please enter a valid Amazon URL.")
    else:
        with st.spinner("Fetching product details from Amazon. This may take a few seconds..."):
            title, price, img_url = scrape_amazon_price(url)
            if not title or price is None:
                st.error("Failed to fetch product details from Amazon. The URL might be invalid or Amazon blocked the request.")
            else:
                success, msg = add_tracked_item(url, title, target_price if target_price > 0 else None, price, img_url)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Error: {msg}")

st.markdown("---")

st.subheader("Currently Tracking")

try:
    items = get_tracked_items()
    if not items:
        st.info("You are not tracking any products yet.")
    else:
        # Display items in a grid layout
        cols = st.columns(3)
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    if item.get("image_url"):
                        st.image(item["image_url"], use_container_width=True)
                    st.markdown(f"**[{item['name']}]({item['url']})**")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Current Price", f"₹{item.get('current_price', 'N/A')}")
                    with col_b:
                        if item.get("target_price"):
                            st.metric("Target Price", f"₹{item['target_price']}")
                        else:
                            st.metric("Target Price", "None")
                            
                    st.caption(f"Last checked: {item.get('last_checked', 'Never')}")
                    
                    if st.button("Stop Tracking", key=f"del_{item['id']}"):
                        delete_tracked_item(item['id'])
                        st.rerun()
except Exception as e:
    st.error(f"Error loading items: {e}")
