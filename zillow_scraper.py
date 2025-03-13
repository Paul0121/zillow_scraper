import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# ScraperAPI Key (Replace with your actual API key)
SCRAPERAPI_KEY = "YOUR_API_KEY_HERE"

# URLs for Zillow searches
ZILLOW_ACTIVE_URL = "https://www.zillow.com/saint-petersburg-fl/"
ZILLOW_SOLD_URL = "https://www.zillow.com/saint-petersburg-fl/sold/"
ZILLOW_OFFMARKET_URL = "https://www.zillow.com/saint-petersburg-fl/off-market/"

# Randomized user-agent headers to avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
]

def get_zillow_data(url, listing_type):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    scraper_url = f"https://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={url}"
    
    try:
        response = requests.get(scraper_url, headers=headers, timeout=10)
        time.sleep(random.randint(5, 15))  # Longer delay to reduce blocking
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []
    
    if response.status_code != 200:
        st.error(f"Failed to retrieve {listing_type} data from Zillow (Status Code: {response.status_code})")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    properties = []
    
    listings = soup.find_all("article")
    for listing in listings:
        try:
            price = listing.find("span", class_="PropertyCardWrapper__StyledPriceLine").text.strip()
            address = listing.find("address").text.strip()
            details = listing.find("ul", class_="PropertyCardWrapper__CardDetails").find_all("li")
            
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
    
    return properties

# Streamlit UI
st.title("Zillow Property Scraper - Saint Petersburg, FL")
if st.button("Run Scraper"):
    st.write("Scraping Zillow for active, sold, and off-market listings...")
    
    data_active = get_zillow_data(ZILLOW_ACTIVE_URL, "Active Listing")
    data_sold = get_zillow_data(ZILLOW_SOLD_URL, "Sold Listing")
    data_offmarket = get_zillow_data(ZILLOW_OFFMARKET_URL, "Off-Market")
    
    all_data = data_active + data_sold + data_offmarket
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df)
        
        # Provide CSV download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "zillow_properties.csv", "text/csv")
    else:
        st.warning("No data retrieved.")
