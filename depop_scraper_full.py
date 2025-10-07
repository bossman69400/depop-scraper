from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

USERNAME = "methhead"  # <-- Change this to your Depop username!

def setup_driver():
    chrome_options = Options()
    # Uncomment below to watch the browser (for debug), but otherwise, keep headless.
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

def clean_price(price_text):
    if not price_text:
        return 0.0
    numbers = re.findall(r'[\d.]+', price_text)
    return float(numbers[0]) if numbers else 0.0

def get_tiles(driver):
    # Load main page and scroll multiple times
    shop_url = f"https://www.depop.com/{USERNAME}/"
    print(f"Visiting {shop_url}")
    driver.get(shop_url)
    time.sleep(6)
    for _ in range(30):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)

    # Get ALL product tiles
    product_tiles = driver.find_elements(By.CSS_SELECTOR, "li.styles_listItem__uQkGy")
    print(f"Found {len(product_tiles)} product tiles on main page.")

    tile_data = []
    for tile in product_tiles:
        try:
            # Listing link
            link_elem = tile.find_element(By.CSS_SELECTOR, "a.styles_unstyledLink__DsttP")
            href = link_elem.get_attribute("href")
            full_url = "https://www.depop.com" + href if href.startswith("/") else href
            
            # Main image
            try:
                main_img_elem = tile.find_element(By.CSS_SELECTOR, "img._mainImage_e5j9l_11")
                img_main = main_img_elem.get_attribute("src")
            except:
                img_main = ""

            # Discounted price (if present)
            try:
                price_elem = tile.find_element(By.CSS_SELECTOR, "p[aria-label='Discounted price']")
                price = clean_price(price_elem.text)
            except:
                price = 0.0
            # Full price (if wanted)
            try:
                full_price_elem = tile.find_element(By.CSS_SELECTOR, "p[aria-label='Full price']")
                full_price = clean_price(full_price_elem.text)
            except:
                full_price = 0.0

            tile_data.append({
                "listing_url": full_url,
                "main_image": img_main,
                "price": price if price else full_price,
            })
        except Exception as e:
            print("Tile error:", e)
    return tile_data

def scrape_listing_details(driver, url):
    time.sleep(1.5)
    driver.get(url)
    time.sleep(2)

    # Check for sold listings
    sold_elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Sold') or contains(text(),'SOLD')]")
    if any(elem.is_displayed() for elem in sold_elements):
        return None

    # Title
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except:
        title = ""

    # Description
    try:
        desc = driver.find_element(By.CSS_SELECTOR, "[data-testid='listing-description']").text.strip()
    except:
        desc = ""

    # Price (double check)
    try:
        price_elem = driver.find_element(By.CSS_SELECTOR, "[aria-label='Discounted price']")
        price = clean_price(price_elem.text)
    except:
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid='listing-price']")
            price = clean_price(price_elem.text)
        except:
            price = 0.0

    # Images (get up to 8)
    images = []
    img_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='cloudfront'], img[src*='depop']")
    for img in img_elements[:8]:
        src = img.get_attribute("src")
        if src and ("cloudfront" in src or "depop" in src):
            clean_src = src.split("?")[0]
            images.append(clean_src)

    return {
        "title": title,
        "desc": desc,
        "price": price,
        "PictureURL": " | ".join(images),
        "image_count": len(images),
        "listing_url": url
    }

def main():
    driver = setup_driver()

    try:
        print("Loading all product tiles...")
        tile_data = get_tiles(driver)
        print(f"Discovered {len(tile_data)} product links. Now scraping full details...")

        listings = []
        for i, tile in enumerate(tile_data):
            url = tile["listing_url"]
            print(f"({i+1}/{len(tile_data)}) Scraping: {url}")
            details = scrape_listing_details(driver, url)
            if details:
                # Optionally, attach the main shop image if listing images are missing
                if not details["PictureURL"] and tile.get("main_image"):
                    details["PictureURL"] = tile["main_image"]
                    details["image_count"] = 1
                listings.append(details)
            else:
                print(f" - Skipped (sold or error)")

        print(f"\nScraped {len(listings)} active listings! Saving to CSV...")
        df = pd.DataFrame(listings)
        df.to_csv("depop_scraped.csv", index=False)
        print("💾 Saved to: depop_scraped.csv")
        print("\n📋 Preview:\n", df[['title', 'price', 'desc', 'image_count']].head(10))
    finally:
        driver.quit()
        print("Done!")

if __name__ == "__main__":
    main()
