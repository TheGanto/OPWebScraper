# main.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_card_data(url):  # ✅ URL passed from GUI
    print(f"Scraping from: {url}")  # helpful for debugging

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    time.sleep(5)

    while True:
        try:
            load_more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Load')]/ancestor::button")))
            print("Clicking:", load_more_btn.text)
            load_more_btn.click()
            time.sleep(2)
        except:
            break

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    card_data = []

    for row in rows:
        try:
            name = row.find_element(By.CSS_SELECTOR, 'td.tcg-table-body__cell--align-left a.pdp-url').text
            right_cells = row.find_elements(By.CSS_SELECTOR, 'td.tcg-table-body__cell--align-right')
            if len(right_cells) >= 2:
                card_number = right_cells[0].text
                price = right_cells[1].text
                card_data.append((name, card_number, price))  # Now appending a tuple
        except Exception as e:
            print(f"Error extracting data: {e}")
            continue

    driver.quit()
    return card_data
