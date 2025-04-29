import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_url TEXT,
                set_name TEXT,
                card_name TEXT,
                card_number TEXT,
                price TEXT,
                last_updated TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating database table: {e}")
    finally:
        conn.close()

def save_card_data(set_url, set_name, cards):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    now = datetime.now().isoformat()

    try:
        # Clear old cards from the same set
        c.execute("DELETE FROM cards WHERE set_url = ?", (set_url,))

        # Prepare bulk insert
        card_data = [(set_url, set_name, name, card_num, price, now) for (name, card_num, price) in cards]
        
        # Bulk insert cards
        c.executemany('''
            INSERT INTO cards (set_url, set_name, card_name, card_number, price, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', card_data)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving card data: {e}")
    finally:
        conn.close()

def load_cards_by_set(set_url):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    try:
        c.execute("SELECT card_name, card_number, price FROM cards WHERE set_url = ?", (set_url,))
        results = c.fetchall()
        return results if results else None
    except sqlite3.Error as e:
        print(f"Error loading card data: {e}")
        return None
    finally:
        conn.close()
