import streamlit as st
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io

def initialize_driver():
    options = Options()
    options.headless = True  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_product_data(product_url, platform):
    driver = initialize_driver()
    driver.get(product_url)
    
    try:
        if platform == "Shopee":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
            price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
            description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
            photo_url = driver.find_element(By.CSS_SELECTOR, 'img._1m1v2g3').get_attribute('src')
        
        elif platform == "Tokopedia":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-1z7w6s2')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'h1.css-1z7w6s2').text
            price = driver.find_element(By.CSS_SELECTOR, 'span.css-o0fgw0').text
            description = driver.find_element(By.CSS_SELECTOR, 'div.css-1c5uq6j').text
            photo_url = driver.find_element(By.CSS_SELECTOR, 'img[data-testid="product-image"]').get_attribute('src')
        
        elif platform == "Bukalapak":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
            price = driver.find_element(By.CSS_SELECTOR, 'span.price').text
            description = driver.find_element(By.CSS_SELECTOR, 'div.description').text
            photo_url = driver.find_element(By.CSS_SELECTOR, 'img.product-image').get_attribute('src')
        
        else:
            raise ValueError("Platform tidak dikenal")

    except Exception as e:
        st.error(f"Error scraping {platform}: {e}")
        product_name, price, description, photo_url = "N/A", "N/A", "N/A", "N/A"
    
    driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Photo URL': [photo_url]
    }
    return pd.DataFrame(data)

def main():
    st.title("Scraping Produk Marketplace")
    
    platform = st.selectbox("Pilih Platform", ["Shopee", "Tokopedia", "Bukalapak"])
    product_urls = st.text_area("Masukkan URL Produk (pisahkan dengan baris baru)")
    
    if st.button("Scrape Data"):
        if product_urls:
            urls = product_urls.splitlines()
            all_data = pd.DataFrame()
            for url in urls:
                if url.strip():
                    scraped_data = scrape_product_data(url.strip(), platform)
                    all_data = pd.concat([all_data, scraped_data], ignore_index=True)
            
            if not all_data.empty:
                st.success("Scraping berhasil!")
                st.write(all_data)
                
                # Save results to CSV
                csv_io = io.StringIO()
                all_data.to_csv(csv_io, index=False)
                csv_io.seek(0)
                
                st.download_button(
                    label="Download CSV",
                    data=csv_io.getvalue(),
                    file_name="scraped_data.csv",
                    mime="text/csv"
                )
            else:
                st.error("Tidak ada data yang ditemukan untuk URL yang diberikan.")
        else:
            st.error("Harap masukkan URL produk")

if __name__ == "__main__":
    main()
