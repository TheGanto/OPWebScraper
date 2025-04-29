import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    
    # Table for scraped cards from each set
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
    
    # Table for user-selected cards (My Cards)
    c.execute('''
        CREATE TABLE IF NOT EXISTS my_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,
            card_number TEXT NOT NULL,
            price TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_card_data(set_url, set_name, cards):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    now = datetime.now().isoformat()

    # Clear old cards from the same set
    c.execute("DELETE FROM cards WHERE set_url = ?", (set_url,))

    for card in cards:
        if isinstance(card, tuple) and len(card) == 3:
            name, card_num, price = card
            c.execute('''
                INSERT INTO cards (set_url, set_name, card_name, card_number, price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (set_url, set_name, name, card_num, price, now))

    conn.commit()
    conn.close()

def load_cards_by_set(set_url):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    c.execute("SELECT card_name, card_number, price FROM cards WHERE set_url = ?", (set_url,))
    results = c.fetchall()
    conn.close()
    return results

# ✅ New: Add a card to My Cards
def add_to_my_cards(card_name, card_number, price):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()

    # Optional: prevent duplicates
    c.execute("SELECT 1 FROM my_cards WHERE card_name=? AND card_number=?", (card_name, card_number))
    if not c.fetchone():
        c.execute('''
            INSERT INTO my_cards (card_name, card_number, price)
            VALUES (?, ?, ?)
        ''', (card_name, card_number, price))
        conn.commit()

    conn.close()

# ✅ New: Load all saved cards from My Cards
def load_my_cards():
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()
    c.execute("SELECT card_name, card_number, price FROM my_cards")
    cards = c.fetchall()
    conn.close()
    return cards
