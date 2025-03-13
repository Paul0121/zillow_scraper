import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a browser
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_zillow(url, listing_type):
    driver = get_driver()
    driver.get(url)
    time.sleep(random.randint(3, 7))  # Random delay to avoid detection
    
    properties = []
    listings = driver.find_elements(By.CSS_SELECTOR, "article")
    
    for listing in listings:
        try:
            price = listing.find_element(By.CSS_SELECTOR, "span[data-test='property-card-price']").text.strip()
            address = listing.find_element(By.CSS_SELECTOR, "address").text.strip()
            details = listing.find_elements(By.CSS_SELECTOR, "ul[data-test='property-card-details'] li")
            
            beds = details[0].text.strip() if len(details) > 0 else "N/A"
            baths = details[1].text.strip() if len(details) > 1 else "N/A"
            sqft = details[2].text.strip() if len(details) > 2 else "N/A"
            
            properties.append({
                "Type": listing_type,
                "Price": price,
                "Address": address,
                "Beds": beds,
                "Baths": baths,
                "SqFt": sqft
            })
        except:
            continue
    
    driver.quit()
    return properties

# Streamlit UI
st.title("Zillow Property Scraper - Saint Petersburg, FL")
if st.button("Run Scraper"):
    st.write("Scraping Zillow for active, sold, and off-market listings...")
    
    active_url = "https://www.zillow.com/saint-petersburg-fl/"
    sold_url = "https://www.zillow.com/saint-petersburg-fl/sold/"
    offmarket_url = "https://www.zillow.com/saint-petersburg-fl/off-market/"
    
    data_active = scrape_zillow(active_url, "Active Listing")
    data_sold = scrape_zillow(sold_url, "Sold Listing")
    data_offmarket = scrape_zillow(offmarket_url, "Off-Market")
    
    all_data = data_active + data_sold + data_offmarket
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df)
        
        # Provide CSV download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "zillow_properties.csv", "text/csv")
    else:
        st.warning("No data retrieved.")
