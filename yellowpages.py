import csv
import json
import random
import time

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def pause(x=0.5, y=1.5):
    time.sleep(random.uniform(x, y))

def type_text(el, txt):
    el.click()
    pause(0.3, 0.7)
    for c in txt:
        el.send_keys(c)
        time.sleep(random.uniform(0.05, 0.15))

opts = uc.ChromeOptions()
opts.add_argument("--start-maximized")
opts.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(version_main=147, options=opts)
wait = WebDriverWait(driver, 20)

driver.get("https://www.yellowpages.com/")
wait.until(EC.presence_of_element_located((By.NAME, "search_terms")))
pause(2.5, 4)

for _ in range(6):
    driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(300, 700))
    pause(0.4, 1.1)

try:
    link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Contact')]")))
    pause()
    link.click()
except TimeoutException:
    print("⚠️ Contact link not found")

pause(2, 3)

driver.back()
wait.until(EC.presence_of_element_located((By.NAME, "search_terms")))
pause(2, 3)

driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
pause(1, 2)

biz = input("Enter Business Type: ").strip()
loc = input("Enter Location: ").strip()

what = wait.until(EC.element_to_be_clickable((By.NAME, "search_terms")))
where = wait.until(EC.element_to_be_clickable((By.NAME, "geo_location_terms")))

what.clear()
where.clear()

type_text(what, biz)
type_text(where, loc)

btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
driver.execute_script("arguments[0].click();", btn)

print("✅ Search executed")

wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'result')]")))
pause(3, 5)

results = []

while True:
    print("📄 Scraping current page...")
    cards = driver.find_elements(By.XPATH, "//div[contains(@class,'result')]")
    print(f"Found {len(cards)} listings")

    for card in cards:
        item = {}
        try:
            try:
                item["name"] = card.find_element(By.XPATH, ".//a[contains(@class,'business-name')]").text.strip()
            except: pass

            try:
                item["phone"] = card.find_element(By.XPATH, ".//div[contains(@class,'phones')]").text.strip()
            except: pass

            try:
                item["address"] = card.find_element(By.XPATH, ".//div[contains(@class,'street-address')]").text.strip()
            except: pass

            try:
                item["rating"] = card.find_element(By.XPATH, ".//div[contains(@class,'ratings')]").text.strip()
            except: pass

            try:
                item["details"] = card.find_element(By.XPATH, ".//div[contains(@class,'categories')]").text.strip()
            except: pass

            try:
                item["website"] = card.find_element(By.XPATH, ".//a[contains(@class,'track-visit-website')]").get_attribute("href")
            except: pass

            if item:
                results.append(item)

        except Exception as e:
            print("Skipping listing:", e)

    try:
        nxt = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'next')]")))
        driver.execute_script("arguments[0].click();", nxt)
        print("➡️ Moving to next page...")
        pause(3, 6)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'result')]")))
    except:
        print("❌ No more pages")
        break

with open("yellowpages.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

with open("yellowpages.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name","phone","address","rating","details","website"])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Saved {len(results)} records")