import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URLs for Zillow searches
ZILLOW_ACTIVE_URL = "https://www.zillow.com/saint-petersburg-fl/"
ZILLOW_SOLD_URL = "https://www.zillow.com/saint-petersburg-fl/sold/"
ZILLOW_OFFMARKET_URL = "https://www.zillow.com/saint-petersburg-fl/off-market/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

def get_zillow_data(url, listing_type):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        st.error(f"Failed to retrieve {listing_type} data from Zillow")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    properties = []
    
    listings = soup.find_all("article")
    for listing in listings:
        try:
            price = listing.find("span", class_="PropertyCardWrapper__StyledPriceLine").text.strip()
            address = listing.find("address").text.strip()
            beds = listing.find("ul", class_="PropertyCardWrapper__CardDetails").find_all("li")[0].text.strip()
            baths = listing.find("ul", class_="PropertyCardWrapper__CardDetails").find_all("li")[1].text.strip()
            sqft = listing.find("ul", class_="PropertyCardWrapper__CardDetails").find_all("li")[2].text.strip()
            
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
