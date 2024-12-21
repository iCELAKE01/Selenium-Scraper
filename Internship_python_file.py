import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configuration
CHROME_DRIVER_PATH = "/path/to/chromedriver"  # Update with the actual path to chromedriver
OUTPUT_FILE = "amazon_best_sellers.json"
USERNAME = "your_email@example.com"  # Replace with your Amazon username
PASSWORD = "your_password"  # Replace with your Amazon password

# Categories to scrape
CATEGORIES = {
    "Kitchen": "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "Shoes": "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "Computers": "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "Electronics": "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
}

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_amazon(driver, username, password):
    driver.get("https://www.amazon.in/ap/signin")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(username)
        driver.find_element(By.ID, "continue").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nav-logo-sprites")))
        print("Login successful")
    except TimeoutException:
        print("Login failed. Please check your credentials or internet connection.")
        driver.quit()
        exit()

def scrape_category(driver, category_url, category_name):
    driver.get(category_url)
    products = []

    for page in range(1, 16):  # Scrape up to 15 pages
        print(f"Scraping page {page} of category: {category_name}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zg-item-immersion"))
            )
            items = driver.find_elements(By.CSS_SELECTOR, ".zg-item-immersion")

            for item in items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    price = item.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    rating = item.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                    images = [img.get_attribute("src") for img in item.find_elements(By.TAG_NAME, "img")]

                    products.append({
                        "Product Name": name,
                        "Product Price": price,
                        "Best Seller Rating": rating,
                        "Category Name": category_name,
                        "All Available Images": images
                    })

                except NoSuchElementException as e:
                    print(f"Error extracting product details: {e}")

            # Navigate to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
                next_button.click()
                time.sleep(2)
            except NoSuchElementException:
                print("No more pages available for this category.")
                break

        except TimeoutException:
            print(f"Error loading page {page} for category: {category_name}")
            break

    return products

def main():
    driver = init_driver()
    login_to_amazon(driver, USERNAME, PASSWORD)

    all_products = []

    for category_name, category_url in CATEGORIES.items():
        print(f"Starting scrape for category: {category_name}")
        category_products = scrape_category(driver, category_url, category_name)
        all_products.extend(category_products)

    # Save data to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)

    print(f"Scraping completed. Data saved to {OUTPUT_FILE}")
    driver.quit()

if __name__ == "__main__":
    main()
