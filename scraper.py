import os
import random
import time
from datetime import datetime

import undetected_chromedriver as uc
from pymongo import MongoClient
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "yellowpages_db")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "businesses")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI environment variable is not set. "
        "Export it or copy .env.example to .env before running the scraper."
    )


def human_delay(a=0.5, b=1.5):
    time.sleep(random.uniform(a, b))


def human_typing(element, text):
    element.click()
    human_delay(0.3, 0.7)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def human_scroll(driver):
    for _ in range(random.randint(4, 10)):
        driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(300, 900))
        time.sleep(random.uniform(0.5, 2))

    if random.random() < 0.4:
        driver.execute_script("window.scrollBy(0,-300)")
        time.sleep(random.uniform(1, 3))


def main():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(options=options, version_main=148, use_subprocess=True)
    wait = WebDriverWait(driver, 30)

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.create_index("unique_key", unique=True)

    try:
        driver.get("https://www.yellowpages.com/")
        max_retries = 5

        for attempt in range(max_retries):
        
            driver.get("https://www.yellowpages.com/")
            time.sleep(10)
        
            page_title = driver.title.lower()
        
            if "522" in page_title or "connection timed out" in page_title:
                print(f"522 detected. Retry {attempt+1}/{max_retries}")
                time.sleep(30)
                continue
            
            break
        human_delay(5, 8)

        search_found = False
        for selector in [
            (By.NAME, "search_terms"),
            (By.ID, "query"),
            (By.CSS_SELECTOR, "input[name='search_terms']"),
            (By.XPATH, "//input[contains(@placeholder,'What')]"),
        ]:
            try:
                WebDriverWait(driver, 15).until(EC.visibility_of_element_located(selector))
                search_found = True
                break
            except TimeoutException:
                continue

        if not search_found:
            raise RuntimeError("Search field not found")

        for _ in range(6):
            driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(300, 700))
            human_delay(0.4, 1.1)

        try:
            contact_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Contact')]")))
            human_delay()
            contact_link.click()
        except TimeoutException:
            print("Contact link not found")

        human_delay(2, 3)
        driver.back()
        wait.until(EC.presence_of_element_located((By.NAME, "search_terms")))
        human_delay(2, 3)
        driver.execute_script("window.scrollTo({top:0,behavior:'smooth'})")

        business = input("Enter Business Type: ").strip()
        location = input("Enter Location: ").strip()

        while True:
            try:
                max_pages = int(input("How many pages do you want to scrape? : "))
                if max_pages > 0:
                    break
            except ValueError:
                pass
            print("Enter valid integer greater than zero")

        what = wait.until(EC.element_to_be_clickable((By.NAME, "search_terms")))
        where = wait.until(EC.element_to_be_clickable((By.NAME, "geo_location_terms")))
        what.clear()
        where.clear()
        human_typing(what, business)
        human_typing(where, location)

        search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        driver.execute_script("arguments[0].click();", search_btn)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'result')]")))

        seen = set()
        page_count, total_saved = 1, 0

        while page_count <= max_pages:
            human_delay(2, 4)
            human_scroll(driver)
            containers = driver.find_elements(By.XPATH, "//div[contains(@class,'result')]")
            if not containers:
                break

            for container in containers:
                data = {}
                for key, xpath, attr in [
                    ("name", ".//a[contains(@class,'business-name')]", "text"),
                    ("phone", ".//div[contains(@class,'phones')]", "text"),
                    ("address", ".//div[contains(@class,'street-address')]", "text"),
                    ("rating", ".//div[contains(@class,'ratings')]", "text"),
                    ("details", ".//div[contains(@class,'categories')]", "text"),
                    ("website", ".//a[contains(@class,'track-visit-website')]", "href"),
                ]:
                    try:
                        el = container.find_element(By.XPATH, xpath)
                        data[key] = el.text.strip() if attr == "text" else el.get_attribute(attr)
                    except Exception:
                        continue

                if not data:
                    continue

                unique_key = data.get("website") or data.get("phone") or f"{data.get('name','')}_{data.get('address','')}"
                if not unique_key or unique_key in seen:
                    continue

                seen.add(unique_key)
                data.update(
                    {
                        "unique_key": unique_key,
                        "search_term": business,
                        "search_location": location,
                        "page_number": page_count,
                        "scraped_at": datetime.utcnow(),
                    }
                )
                collection.update_one({"unique_key": unique_key}, {"$set": data}, upsert=True)
                total_saved += 1

            if page_count % 3 == 0:
                time.sleep(random.randint(25, 60))
            if page_count >= max_pages:
                break

            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'next')]")))
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(random.uniform(8, 20))
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'result')]")))
                page_count += 1
            except Exception:
                break

        print(f"Saved records: {total_saved}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        client.close()


if __name__ == "__main__":
    main()