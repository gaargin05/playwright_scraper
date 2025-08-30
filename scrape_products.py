import json
import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://hiring.idenhq.com/challenge"
USERNAME = "gaargin2004@gmail.com"  
PASSWORD = "Zkbodxvm"    
SESSION_FILE = "auth.json"


def save_session(context):
    context.storage_state(path=SESSION_FILE)


def ensure_logged_in(page):
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    
    if page.locator("input[name='email']").count() > 0:
        print("[INFO] Logging in...")
        page.fill("input[name='email']", USERNAME)
        page.fill("input[name='password']", PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_selector("text=Open Options")
        print("[INFO] Login successful")
    else:
        print("[INFO] Already logged in")


def navigate_to_table(page):
    print("[INFO] Navigating to product table...")
    page.click("text='Open Options'")
    page.wait_for_selector("text='Inventory'")
    page.click("text='Inventory'")
    page.wait_for_selector("text='Access Detailed View'")
    page.click("text='Access Detailed View'")
    page.wait_for_selector("text='Show Full Product Table'")
    page.click("text='Show Full Product Table'")
    page.wait_for_selector("table")  
    print("[INFO] Table is visible now.")


def extract_table_data(page):
    print("[INFO] Extracting product data from table...")
    products = []

    while True:
        rows = page.locator("table tbody tr")
        row_count = rows.count()

        for i in range(row_count):
            cells = rows.nth(i).locator("td")
            data = [cells.nth(j).inner_text() for j in range(cells.count())]
            products.append(data)

        
        next_btn = page.locator("text=Next")
        if next_btn.is_enabled():
            next_btn.click()
            page.wait_for_timeout(1500)  
        else:
            break

    return products


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if os.path.exists(SESSION_FILE):
            context = browser.new_context(storage_state=SESSION_FILE)
        else:
            context = browser.new_context()
        page = context.new_page()

        ensure_logged_in(page)
        navigate_to_table(page)
        save_session(context)

        products = extract_table_data(page)

        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)

        print(f"[INFO] Extracted {len(products)} products. Data saved in products.json")

        browser.close()


if __name__ == "__main__":
    main()
