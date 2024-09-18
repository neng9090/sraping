import streamlit as st
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import io

def initialize_driver():
    options = Options()
    options.headless = True  # Mode headless untuk menjalankan Chrome tanpa UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_shopee(product_url):
    driver = initialize_driver()
    driver.get(product_url)
    
    try:
        # Tunggu elemen untuk produk dimuat dengan benar
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
        
        # Ambil data produk
        product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
        price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
        description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
    except Exception as e:
        st.error(f"Error scraping Shopee: {e}")
        product_name, price, description = "N/A", "N/A", "N/A"
    
    driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description]
    }
    return pd.DataFrame(data)

def scrape_tokopedia(product_url):
    driver = initialize_driver()
    driver.get(product_url)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-1z7w6s2')))
        
        # Ambil data produk
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.css-1z7w6s2').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.css-o0fgw0').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.css-1c5uq6j').text
    except Exception as e:
        st.error(f"Error scraping Tokopedia: {e}")
        product_name, price, description = "N/A", "N/A", "N/A"
    
    driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description]
    }
    return pd.DataFrame(data)

def scrape_bukalapak(product_url):
    driver = initialize_driver()
    driver.get(product_url)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title')))
        
        # Ambil data produk
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.price').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.description').text
    except Exception as e:
        st.error(f"Error scraping Bukalapak: {e}")
        product_name, price, description = "N/A", "N/A", "N/A"
    
    driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description]
    }
    return pd.DataFrame(data)

def main():
    st.title("Scraping Produk Marketplace")
    
    platform = st.selectbox("Pilih Platform", ["Shopee", "Tokopedia", "Bukalapak"])
    product_url = st.text_input("Masukkan URL Produk")
    
    if st.button("Scrape Data"):
        if product_url:
            if platform == "Shopee":
                scraped_data = scrape_shopee(product_url)
            elif platform == "Tokopedia":
                scraped_data = scrape_tokopedia(product_url)
            elif platform == "Bukalapak":
                scraped_data = scrape_bukalapak(product_url)
            else:
                st.error("Platform tidak dikenal")
                return
            
            if not scraped_data.empty:
                st.success("Scraping berhasil!")
                st.write(scraped_data)
                
                # Simpan hasil scraping ke CSV
                csv_io = io.StringIO()
                scraped_data.to_csv(csv_io, index=False)
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
