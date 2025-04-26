from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Load page
url = "https://www.tcgplayer.com/categories/trading-and-collectible-card-games/one-piece-card-game/price-guides/royal-blood"
driver.get(url)
time.sleep(5)

# Click all "Load More" buttons
while True:
    try:
        load_more_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[contains(text(), 'Load')]/ancestor::button"
        )))
        print("Clicking:", load_more_btn.text)
        load_more_btn.click()
        time.sleep(2)
    except:
        break

# Grab all table rows
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

# Loop through each row and extract name, number, and price
print("\nCard Data:")
for row in rows:
    try:
        name = row.find_element(By.CSS_SELECTOR, 'td.tcg-table-body__cell--align-left a.pdp-url').text
        
        # Find all right-aligned <td>s
        right_cells = row.find_elements(By.CSS_SELECTOR, 'td.tcg-table-body__cell--align-right')
        if len(right_cells) >= 2:
            card_number = right_cells[0].text
            price = right_cells[1].text
            print(f"{name} | Card #: {card_number} | Price: {price}")
        else:
            print(f"{name} | Incomplete data")
    except Exception as e:
        continue

# Close browser
driver.quit()
