import tkinter as tk
from tkinter import messagebox, ttk
import requests
import sqlite3
import xml.etree.ElementTree as ET
from main import scrape_card_data
from database import init_db, save_card_data, load_cards_by_set, add_to_my_cards, load_my_cards
from export import export_my_cards_to_csv, export_my_cards_to_pdf  # Import export functions

# Dark theme color palette
BG_COLOR = '#1e1e1e'
TEXT_COLOR = '#ffffff'
ROW_ODD = '#2a2a2a'
ROW_EVEN = '#1e1e1e'
BUTTON_BG = '#3a3a3a'
BUTTON_HOVER = '#505050'

# Initialize the database
init_db()

urls = []
my_cards_collection = []  # In-memory collection of "My Cards"

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
        selected_full_url = next((url for url, name in urls if name == selected_card_name), None)

        if selected_full_url:
            cards = load_cards_by_set(selected_full_url)
            if cards:
                display_cards(cards)
            else:
                card_data = scrape_card_data(selected_full_url)
                save_card_data(selected_full_url, selected_card_name, card_data)
                display_cards(card_data)

def display_cards(cards):
    for row in tree.get_children():
        tree.delete(row)

    if cards:
        for index, (name, card_num, price) in enumerate(cards):
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(name, card_num, price), tags=(row_tag,))
        sort_cards_by_price()
    else:
        messagebox.showinfo("Info", "No cards found.")

def sort_cards_by_price():
    rows = [(tree.item(item)['values'][2], item) for item in tree.get_children()]
    
    # Update the lambda to handle commas in price strings
    rows.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '').strip()) if x[0] != 'N/A' else 0, reverse=sort_order.get())
    
    for index, (price, item) in enumerate(rows):
        tree.move(item, '', index)

    # Toggle sorting order
    sort_order.set(not sort_order.get())

# Function to open the "My Cards" window
# Function to open the "My Cards" window
def open_my_cards_window():
    # Fetch all the cards from the database
    my_cards_collection = load_my_cards()
    
    # Open the window
    my_cards_window = tk.Toplevel(root)
    my_cards_window.title("My Cards")
    my_cards_window.geometry("600x400")
    my_cards_window.configure(bg=BG_COLOR)

    label = tk.Label(my_cards_window, text="My Cards Collection", font=("Helvetica", 14), bg=BG_COLOR, fg=TEXT_COLOR)
    label.pack(pady=20)

    # Check if there are cards in the collection
    if not my_cards_collection:
        label = tk.Label(my_cards_window, text="No cards in My Cards collection.", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack()
    else:
        # Display cards from the collection
        for card in my_cards_collection:
            card_name, card_number, price = card
            card_text = f"{card_name} ({card_number}) - {price}"

            card_frame = tk.Frame(my_cards_window, bg=BG_COLOR)
            card_frame.pack(pady=5, fill="x")

            card_label = tk.Label(card_frame, text=card_text, font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
            card_label.pack(side="left", padx=10)

            delete_button = tk.Button(
    card_frame,
    text="Delete",
    command=lambda c=card, f=card_frame: delete_card_from_my_cards(c, f),
    bg="#ff4d4d",
    fg=TEXT_COLOR,
    activebackground="#ff1a1a",
    font=("Helvetica", 10, "bold")
)
            delete_button.pack(side="right", padx=10)

    close_button = tk.Button(my_cards_window, text="Close", command=my_cards_window.destroy)
    style_button(close_button)
    close_button.pack(pady=10)




# Function to handle card selection and confirmation
def on_card_select(event):
    selected_item = tree.selection()
    if selected_item:
        # Get the values from the selected row
        selected_card_name = tree.item(selected_item[0])['values'][0]
        selected_card_num = tree.item(selected_item[0])['values'][1]
        selected_card_price = tree.item(selected_item[0])['values'][2]
        
        # Ask if they want to add the card to My Cards
        response = messagebox.askyesno(
            "Add Card to My Cards",
            f"Do you want to add {selected_card_name} ({selected_card_num}) - {selected_card_price} to your My Cards collection?"
        )

        if response:
            # Add the card to the database
            add_to_my_cards(selected_card_name, selected_card_num, selected_card_price)
            messagebox.showinfo("Success", f"{selected_card_name} has been added to your My Cards collection.")



def style_button(button):
    button.config(
        font=("Helvetica", 12, "bold"),
        bg=BUTTON_BG,
        fg=TEXT_COLOR,
        relief="flat",
        height=2,
        width=15
    )
    button.bind("<Enter>", lambda e: button.config(bg=BUTTON_HOVER))
    button.bind("<Leave>", lambda e: button.config(bg=BUTTON_BG))

# GUI setup
root = tk.Tk()
root.title("One Piece Card Price Viewer")
root.geometry("850x600")
root.configure(bg=BG_COLOR)

canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.config(yscrollcommand=scrollbar.set)

content_frame = tk.Frame(canvas, bg=BG_COLOR)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

def on_frame_configure(event):
    canvas.config(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", on_frame_configure)

header = tk.Label(content_frame, text="One Piece Card Price Viewer", font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
header.pack(pady=20)

frame_urls = tk.Frame(content_frame, bg=BG_COLOR)
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
url_tree.tag_configure('oddrow', background=ROW_ODD, foreground=TEXT_COLOR)
url_tree.tag_configure('evenrow', background=ROW_EVEN, foreground=TEXT_COLOR)

frame = tk.Frame(content_frame, bg=BG_COLOR, height=300)
frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Card Name", "Card #", "Price")
tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
tree.pack(side="left", fill="both", expand=True)

tree_scroll = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree_scroll.pack(side="right", fill="y")
tree.config(yscrollcommand=tree_scroll.set)

tree.tag_configure('oddrow', background=ROW_ODD, foreground=TEXT_COLOR)
tree.tag_configure('evenrow', background=ROW_EVEN, foreground=TEXT_COLOR)

tree.column("Card Name", width=400, anchor="w")
tree.column("Card #", width=150, anchor="center")
tree.column("Price", width=150, anchor="e")

tree.heading("#1", text="Card Name", anchor="w")
tree.heading("#2", text="Card #", anchor="w")
tree.heading("#3", text="Price", anchor="w", command=sort_cards_by_price)
def delete_card_from_db(card_name, card_number):
    conn = sqlite3.connect("cards.db")
    c = conn.cursor()

    # Delete the card from the 'my_cards' table
    c.execute("DELETE FROM my_cards WHERE card_name=? AND card_number=?", (card_name, card_number))
    conn.commit()
    conn.close()
def delete_card_from_my_cards(card, card_frame):
    card_name, card_number, _ = card

    # Delete from database
    delete_card_from_db(card_name, card_number)

    # Remove the card's frame from the window
    card_frame.destroy()

    # Show success message
    messagebox.showinfo("Deleted", f"{card_name} has been removed from your collection.")


  



# My Cards button (opens new window)
my_cards_button = tk.Button(content_frame, text="My Cards", command=open_my_cards_window)
style_button(my_cards_button)
my_cards_button.pack(pady=20)

# Export buttons (CSV and PDF)
export_csv_button = tk.Button(content_frame, text="Export Cards-CSV", command=export_my_cards_to_csv)
style_button(export_csv_button)
export_csv_button.pack(pady=20)

export_pdf_button = tk.Button(content_frame, text="Export Cards-PDF", command=export_my_cards_to_pdf)
style_button(export_pdf_button)
export_pdf_button.pack(pady=20)

# Bind row click to select card and confirm
tree.bind("<ButtonRelease-1>", on_card_select)

# Initialize sorting state
sort_order = tk.BooleanVar(value=False)

# Initial fetch
fetch_urls()

# Launch app
root.mainloop()
