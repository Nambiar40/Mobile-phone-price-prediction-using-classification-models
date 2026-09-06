from supabase import create_client, Client
import sqlite3
import os
import datetime

# Try to use Supabase, fallback to SQLite if not configured
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

# SQLite fallback config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'history.db')

def get_supabase_client() -> Client:
    if not USE_SUPABASE:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_sqlite_db():
    if not USE_SUPABASE:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_type TEXT,
                    brand TEXT,
                    model_name TEXT,
                    predicted_price TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS price_tracker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    platform TEXT,
                    product_name TEXT,
                    target_price REAL,
                    current_price REAL,
                    image_url TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_checked DATETIME
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT,
                    type TEXT,
                    read_status BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

init_sqlite_db()

# --- Database Interface Functions ---

def insert_search_history(prediction_type, brand, model_name, predicted_price):
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            supabase.table('search_history').insert({
                "prediction_type": prediction_type,
                "brand": brand,
                "model_name": model_name,
                "predicted_price": predicted_price
            }).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO search_history (prediction_type, brand, model_name, predicted_price)
                VALUES (?, ?, ?, ?)
            ''', (prediction_type, brand, model_name, predicted_price))
            conn.commit()

def get_search_history(limit=50):
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            response = supabase.table('search_history').select("*").order("timestamp", desc=True).limit(limit).execute()
            # Remap keys for frontend compatibility
            res = []
            for r in response.data:
                res.append({
                    'id': r['id'],
                    'type': r['prediction_type'],
                    'brand': r['brand'],
                    'model_name': r['model_name'],
                    'price': r['predicted_price'],
                    'date': r['timestamp']
                })
            return res
        except Exception as e:
            print(f"Supabase error: {e}")
            return []
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, prediction_type, brand, model_name, predicted_price, timestamp FROM search_history ORDER BY timestamp DESC LIMIT ?', (limit,))
            rows = c.fetchall()
            return [{'id': r[0], 'type': r[1], 'brand': r[2], 'model_name': r[3], 'price': r[4], 'date': r[5]} for r in rows]

def add_tracked_item(url, title, target_price, price, img_url, platform="Amazon"):
    if USE_SUPABASE:
        supabase = get_supabase_client()
        try:
            # Check if URL exists
            existing = supabase.table('price_tracker').select("id").eq("url", url).execute()
            if existing.data:
                return False, "This URL is already being tracked."
                
            supabase.table('price_tracker').insert({
                "url": url,
                "platform": platform,
                "product_name": title,
                "target_price": target_price,
                "current_price": price,
                "image_url": img_url,
                "last_checked": datetime.datetime.now().isoformat()
            }).execute()
            
            insert_notification(f"Started tracking {title[:30]}... at ₹{price}", "info")
            insert_search_history("Price Tracker", platform, title[:50], f"Rs.{price}" if price else "N/A")
            return True, "Product added to tracker!"
        except Exception as e:
            return False, str(e)
    else:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO price_tracker (url, platform, product_name, target_price, current_price, image_url, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (url, platform, title, target_price, price, img_url))
                conn.commit()
                insert_notification(f"Started tracking {title[:30]}... at ₹{price}", "info")
                insert_search_history("Price Tracker", platform, title[:50], f"Rs.{price}" if price else "N/A")
                return True, "Product added to tracker!"
        except sqlite3.IntegrityError:
            return False, "This URL is already being tracked."
        except Exception as e:
            return False, str(e)

def get_tracked_items():
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            response = supabase.table('price_tracker').select("*").eq("is_active", True).order("created_at", desc=True).execute()
            # Remap
            res = []
            for r in response.data:
                res.append({
                    'id': r['id'],
                    'url': r['url'],
                    'platform': r['platform'],
                    'name': r['product_name'],
                    'target_price': r['target_price'],
                    'current_price': r['current_price'],
                    'image_url': r['image_url'],
                    'last_checked': r['last_checked']
                })
            return res
        except Exception as e:
            print(f"Supabase error: {e}")
            return []
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, url, platform, product_name, target_price, current_price, image_url, last_checked FROM price_tracker WHERE is_active = 1 ORDER BY created_at DESC')
            rows = c.fetchall()
            return [{'id': r[0], 'url': r[1], 'platform': r[2], 'name': r[3], 'target_price': r[4], 'current_price': r[5], 'image_url': r[6], 'last_checked': r[7]} for r in rows]

def update_tracked_price(item_id, new_price):
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            supabase.table('price_tracker').update({
                "current_price": new_price,
                "last_checked": datetime.datetime.now().isoformat()
            }).eq("id", item_id).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('UPDATE price_tracker SET current_price = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?', (new_price, item_id))
            conn.commit()

def delete_tracked_item(item_id):
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            supabase.table('price_tracker').delete().eq("id", item_id).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM price_tracker WHERE id = ?', (item_id,))
            conn.commit()

def insert_notification(message, n_type):
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            supabase.table('notifications').insert({
                "message": message,
                "type": n_type,
                "read_status": False
            }).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO notifications (message, type) VALUES (?, ?)', (message, n_type))
            conn.commit()

def get_unread_notifications():
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            response = supabase.table('notifications').select("*").eq("read_status", False).order("created_at", desc=True).limit(20).execute()
            return response.data
        except Exception as e:
            print(f"Supabase error: {e}")
            return []
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, message, type, created_at FROM notifications WHERE read_status = 0 ORDER BY created_at DESC LIMIT 20')
            rows = c.fetchall()
            return [{'id': r[0], 'message': r[1], 'type': r[2], 'created_at': r[3]} for r in rows]

def mark_notifications_read(ids):
    if not ids: return
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            for n_id in ids:
                supabase.table('notifications').update({"read_status": True}).eq("id", n_id).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    else:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            c.execute(f'UPDATE notifications SET read_status = 1 WHERE id IN ({placeholders})', ids)
            conn.commit()
