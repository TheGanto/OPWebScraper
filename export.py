import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from database import load_my_cards

# Export "My Cards" collection to CSV
def export_my_cards_to_csv():
    # Get cards from the database
    cards = load_my_cards()

    # Specify CSV file name
    filename = "my_cards.csv"

    # Write to CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Card Name", "Card Number", "Price"])  # Header row

        for card in cards:
            writer.writerow(card)  # Write each card

    print(f"Exported {len(cards)} cards to {filename}.")

# Export "My Cards" collection to PDF
def export_my_cards_to_pdf():
    # Get cards from the database
    cards = load_my_cards()

    # Create a PDF file
    filename = "my_cards.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Set up the initial Y position for text
    y_position = 750
    c.drawString(30, y_position, "My Cards Collection")
    y_position -= 20

    # Write card data to the PDF
    for card in cards:
        c.drawString(30, y_position, f"Card Name: {card[0]}, Card Number: {card[1]}, Price: {card[2]}")
        y_position -= 15

        # If the text gets too long, create a new page
        if y_position < 50:
            c.showPage()  # Start a new page
            c.setFont("Helvetica", 12)  # Reset font size
            y_position = 750  # Reset Y position

    # Save the PDF file
    c.save()

    print(f"Exported {len(cards)} cards to {filename}.")
