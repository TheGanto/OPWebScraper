# gui.py

import tkinter as tk
from tkinter import messagebox, ttk
from main import scrape_card_data

# Function to fetch and display the card data
def fetch_and_display():
    # Disable the search button and entry while loading cards
    search_button.config(state="disabled")
    search_entry.config(state="disabled")

    # Clear existing table data
    for row in tree.get_children():
        tree.delete(row)

    try:
        # Scrape the data once and store it in the cache
        cards = scrape_card_data()

        if cards:
            # Insert rows into the table
            for index, line in enumerate(cards):
                if " | Card #:" in line and " | Price:" in line:
                    name_part = line.split(" | Card #:")[0]
                    card_num = line.split(" | Card #:")[1].split(" | Price:")[0]
                    price = line.split(" | Price:")[1].strip()

                    # Clean up the price string: remove dollar sign and any non-numeric characters except '.'
                    price_cleaned = price.replace('$', '').strip()

                    try:
                        # Try to convert price to float
                        price_value = float(price_cleaned)
                    except ValueError:
                        price_value = 0.00  # Default to 0.00 if price is invalid
                    
                    # Apply price coloring based on value
                    price_color = "green" if price_value > 1 else "red"
                    
                    # Insert row in the table
                    row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                    tree.insert("", "end", values=(name_part, card_num, price), tags=(row_tag,))
                    
                    # Apply price color
                    tree.tag_configure('price', foreground=price_color)

            # Enable the search bar and button after loading cards
            search_button.config(state="normal")
            search_entry.config(state="normal")
        else:
            messagebox.showinfo("Info", "No cards found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load cards: {e}")

# Function to search and filter cards
def search_cards():
    search_term = search_var.get().lower()

    # Clear existing table data
    for row in tree.get_children():
        tree.delete(row)

    try:
        # Scrape the data again each time a search is performed
        cards = scrape_card_data()

        if cards:
            for index, line in enumerate(cards):
                if " | Card #:" in line and " | Price:" in line:
                    name_part = line.split(" | Card #:")[0]
                    card_num = line.split(" | Card #:")[1].split(" | Price:")[0]
                    price = line.split(" | Price:")[1].strip()

                    # Clean up the price string: remove dollar sign and any non-numeric characters except '.'
                    price_cleaned = price.replace('$', '').strip()

                    try:
                        # Try to convert price to float
                        price_value = float(price_cleaned)
                    except ValueError:
                        price_value = 0.00  # Default to 0.00 if price is invalid

                    # If the search term matches the card name or card number, display it
                    if search_term in name_part.lower() or search_term in card_num:
                        # Apply price coloring based on value
                        price_color = "green" if price_value > 1 else "red"
                        
                        # Insert row in the table
                        row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                        tree.insert("", "end", values=(name_part, card_num, price), tags=(row_tag,))
                        
                        # Apply price color
                        tree.tag_configure('price', foreground=price_color)
        else:
            messagebox.showinfo("Info", "No cards found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load cards: {e}")

# Function to sort the table by column
def sort_column(treeview, column, reverse=False):
    # Get all items in the treeview
    data = [(treeview.item(item)["values"], item) for item in treeview.get_children()]

    # Sort data based on the specified column (0 for Card Name, 1 for Card #, 2 for Price)
    if column == 2:  # Sorting by price
        data.sort(key=lambda x: float(x[0][column].replace('$', '').strip()), reverse=reverse)
    else:
        data.sort(key=lambda x: x[0][column], reverse=reverse)

    # Reinsert the sorted data into the treeview
    for index, (values, item) in enumerate(data):
        treeview.item(item, values=values)

    # Return the reverse flag for toggling sort order
    return not reverse

# Create main window
root = tk.Tk()
root.title("One Piece Card Price Viewer")
root.geometry("850x600")
root.resizable(True, True)

# Set background color
root.configure(bg='#F0F8FF')  # Light blue background

# Scrape button with custom style
scrape_button = tk.Button(root, text="Load Card Prices", font=('Arial', 14, 'bold'),
                          bg='#4CAF50', fg='white', relief="flat", height=2, width=20,
                          command=fetch_and_display)
scrape_button.pack(pady=20)

# Hover effect for the button (requires tkinter's event binding)
def on_enter(e):
    scrape_button['bg'] = '#45a049'

def on_leave(e):
    scrape_button['bg'] = '#4CAF50'

scrape_button.bind("<Enter>", on_enter)
scrape_button.bind("<Leave>", on_leave)

# Search bar to filter results
search_var = tk.StringVar()

# Search label, entry, and button
search_label = tk.Label(root, text="Search Card:", font=('Arial', 12), bg='#F0F8FF')
search_entry = tk.Entry(root, textvariable=search_var, font=('Arial', 12), width=25)
search_button = tk.Button(root, text="Search", font=('Arial', 12, 'bold'), bg='#2196F3', fg='white', command=search_cards)

# Initially disable the search bar and button
search_entry.config(state="disabled")
search_button.config(state="disabled")

# Pack the search widgets under the "Load Card Prices" button
search_label.pack(pady=5)
search_entry.pack(pady=5)
search_button.pack(pady=10)

# Frame for Treeview and Scrollbars
frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create treeview table with columns
columns = ("Card Name", "Card #", "Price")
tree = ttk.Treeview(frame, columns=columns, show="headings", height=25)
tree.pack(side="left", fill="both", expand=True)

# Scrollbar for Treeview
tree_scroll = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree_scroll.pack(side="right", fill="y")
tree.config(yscrollcommand=tree_scroll.set)

# Style the treeview for better presentation
tree.tag_configure('oddrow', background="#f0f0f0")  # Light gray for odd rows
tree.tag_configure('evenrow', background="#ffffff")  # White for even rows
tree.column("Card Name", width=300, anchor="w")
tree.column("Card #", width=100, anchor="center")
tree.column("Price", width=100, anchor="e")

# Style headers
tree.heading("#1", text="Card Name", anchor="w", command=lambda: toggle_sort(tree, 0))
tree.heading("#2", text="Card #", anchor="w", command=lambda: toggle_sort(tree, 1))
tree.heading("#3", text="Price", anchor="w", command=lambda: toggle_sort(tree, 2))

# Sort state variables
sort_reverse = {0: False, 1: False, 2: False}  # Track sort direction for each column

# Function to toggle sorting direction
def toggle_sort(treeview, column):
    reverse = sort_reverse[column]
    sort_reverse[column] = not reverse  # Toggle sort direction
    sort_column(treeview, column, reverse)

# Run the app
root.mainloop()
