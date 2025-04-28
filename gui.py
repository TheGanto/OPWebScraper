# gui.py

import tkinter as tk
from tkinter import messagebox, ttk
import requests
import xml.etree.ElementTree as ET
from main import scrape_card_data

# Store full URLs with display names
urls = []

def fetch_urls():
    try:
        response = requests.get('https://www.tcgplayer.com/sitemap/one-piece-card-game.0.xml')
        response.raise_for_status()
        response.encoding = 'utf-8'

        root = ET.fromstring(response.text)
        namespaces = {'ns0': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls.clear()
        for url in root.findall(".//ns0:url", namespaces=namespaces):
            loc = url.find("ns0:loc", namespaces=namespaces)
            if loc is not None:
                url_text = loc.text
                if url_text.startswith("https://www.tcgplayer.com/categories/trading-and-collectible-card-games/one-piece-card-game/price-guides/"):
                    card_name = url_text.split("/")[-1]
                    urls.append((url_text, card_name))

        for row in url_tree.get_children():
            url_tree.delete(row)

        for full_url, card_name in urls:
            url_tree.insert("", "end", values=(card_name,))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch URLs: {e}")

def select_url(event):
    selected_item = url_tree.selection()
    if selected_item:
        selected_card_name = url_tree.item(selected_item[0])['values'][0]
        selected_full_url = None
        for full_url, name in urls:
            if name == selected_card_name:
                selected_full_url = full_url
                break
        if selected_full_url:
            print(f"Selected URL: {selected_full_url}")
            card_data = scrape_card_data(selected_full_url)
            display_cards(card_data)

def display_cards(cards):
    for row in tree.get_children():
        tree.delete(row)
    if cards:
        for index, line in enumerate(cards):
            if " | Card #:" in line and " | Price:" in line:
                name_part = line.split(" | Card #:")[0]
                card_num = line.split(" | Card #:")[1].split(" | Price:")[0]
                price = line.split(" | Price:")[1].strip()

                price_cleaned = price.replace('$', '').strip()
                try:
                    price_value = float(price_cleaned)
                except ValueError:
                    price_value = 0.00
                row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                tree.insert("", "end", values=(name_part, card_num, price), tags=(row_tag,))
    else:
        messagebox.showinfo("Info", "No cards found.")

# GUI setup
root = tk.Tk()
root.title("One Piece Card Price Viewer")
root.geometry("850x600")
root.configure(bg='#F0F8FF')

frame_urls = tk.Frame(root)
frame_urls.pack(fill="both", expand=True, padx=10, pady=10)

url_columns = ("URLs",)
url_tree = ttk.Treeview(frame_urls, columns=url_columns, show="headings", height=10)
url_tree.pack(side="left", fill="both", expand=True)

url_tree_scroll = tk.Scrollbar(frame_urls, orient="vertical", command=url_tree.yview)
url_tree_scroll.pack(side="right", fill="y")
url_tree.config(yscrollcommand=url_tree_scroll.set)

url_tree.column("URLs", width=800, anchor="w")
url_tree.heading("#1", text="URLs", anchor="w")

url_tree.bind("<<TreeviewSelect>>", select_url)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Card Name", "Card #", "Price")
tree = ttk.Treeview(frame, columns=columns, show="headings", height=25)
tree.pack(side="left", fill="both", expand=True)

tree_scroll = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree_scroll.pack(side="right", fill="y")
tree.config(yscrollcommand=tree_scroll.set)

tree.tag_configure('oddrow', background="#f0f0f0")
tree.tag_configure('evenrow', background="#ffffff")

tree.column("Card Name", width=300, anchor="w")
tree.column("Card #", width=100, anchor="center")
tree.column("Price", width=100, anchor="e")

tree.heading("#1", text="Card Name", anchor="w")
tree.heading("#2", text="Card #", anchor="w")
tree.heading("#3", text="Price", anchor="w")

fetch_urls()
root.mainloop()
