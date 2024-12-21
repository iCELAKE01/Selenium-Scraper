import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Set up Edge options
options = Options()
options.add_argument("--start-maximized")

# Path to your Edge WebDriver
service = Service(r'C:\Users\prath\Softwares\edgedriver_win32\msedgedriver.exe')  # Update with your Edge WebDriver path
driver = webdriver.Edge(service=service, options=options)

# Amazon credentials
AMAZON_EMAIL = 'your_email@example.com'  # Replace with your Amazon email
AMAZON_PASSWORD = 'your_password'          # Replace with your Amazon password

# Function to log in to Amazon
def login_to_amazon():
    driver.get('https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0')
    time.sleep(2)
    
    email_input = driver.find_element(By.ID, 'ap_email')
    email_input.send_keys(AMAZON_EMAIL)
    email_input.send_keys(Keys.RETURN)
    time.sleep(2)
    
    password_input = driver.find_element(By.ID, 'ap_password')
    password_input.send_keys(AMAZON_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

# Function to scrape product details
def scrape_best_sellers(category_url):
    driver.get(category_url)
    time.sleep(3)
    
    products = []
    
    # Loop through the products on the page
    for product in driver.find_elements(By.CSS_SELECTOR, '.zg-item-immersion'):
        try:
            name = product.find_element(By.CSS_SELECTOR, '.p13n-sc-truncate').text
            price = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price').text
            discount = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price').get_attribute('data-discount')
            rating = product.find_element(By.CSS_SELECTOR, '.a-icon-alt').text
            sold_by = product.find_element(By.CSS_SELECTOR, '.a-size-small.a-color-secondary').text
            description = product.find_element(By.CSS_SELECTOR, '.a-size-small.a-color-secondary').text
            images = [img.get_attribute('src') for img in product.find_elements(By.CSS_SELECTOR, 'img')]
            
            products.append({
                'Product Name': name,
                'Product Price': price,
                'Sale Discount': discount,
                'Best Seller Rating': rating,
                'Sold By': sold_by,
                'Product Description': description,
                'Images': images
            })
        except NoSuchElementException:
            continue
    
    return products

# Main function
def main():
    login_to_amazon()
    
    categories = [
        'https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0',
        'https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0',
        'https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0',
        'https://www.amazon.in/gp/bestsellers/electronics/ref=zq_bs_nav_electronics_0',
        # Add more category URLs as needed
    ]
    
    all_products = []
    
    for category in categories:
        products = scrape_best_sellers(category)
        all_products.extend(products)
    
    # Save to CSV
    with open('amazon_best_sellers.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = all_products[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_products)
    
    # Save to JSON
    with open('amazon_best_sellers.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(all_products, jsonfile, ensure_ascii=False, indent=4)
    
    driver.quit()

if __name__ == "__main__":
    main()