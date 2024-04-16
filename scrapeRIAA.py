import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import numpy as np
from bs4 import BeautifulSoup
import time
import gc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

class WebDriverContextManager:
    def __enter__(self):
        print("Starting the WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 2,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2
        })

        chromedriver_path = r'C:\Users\S00190873\Downloads\chromedriver_win32\chromedriver.exe'
        self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        print("WebDriver closed.")
        gc.collect()

class GoldPlatinumArtistsRIAA:
    def __init__(self, driver):
        self.driver = driver

    def fetch_data(self):
        counter = 0
        print("Navigating to the RIAA website...")
        self.driver.get('https://www.riaa.com/gold-platinum/?advance_search=1&tab_active=awards_by_album&awardal=D&formatal=Single&typeal=&type_optional=ST#search_section')
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='footer-content']")))
        print("Website loaded. Attempting to load more records...")

        try:
            while True:
                button = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.ID, 'loadmore')))
                action = ActionChains(self.driver)
                action.move_to_element(button).click().perform()
                counter += 1
                print(f"{counter}: Clicking the Load More Button...")
                time.sleep(1)
        except:
                False

        counter = 0
        format_details_links = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='format_details']/a")))        
        for link in format_details_links:
            action = ActionChains(self.driver)
            action.move_to_element(link).click().perform()
            counter += 1
            print(f"{counter}: Clicking the More Details Link...")
            time.sleep(1)

        time.sleep(30)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        data = [{
        "Artist": row.select_one('.artists_cell').text.strip(),
        "Title": row.select_one('.others_cell').text.strip(),
        "Units": int(row.select_one('.format_cell').text.replace('MORE DETAILS', '').strip()),
        "Release Date": row.find_next_sibling('tr').select_one('.upper_style').text.strip() if row.find_next_sibling('tr') and row.find_next_sibling('tr').select_one('.upper_style') else 'Not Available',
        "Genre": row.find_next_sibling('tr').select_one('.content_recent_table .col-md-3:nth-of-type(5)').text.strip() if row.find_next_sibling('tr') and row.find_next_sibling('tr').select_one('.content_recent_table .col-md-3:nth-of-type(5)') else 'Not Available' 
        } for row in soup.select('.table_award_row')]

        df = pd.DataFrame(data)
        df['Award'] = np.select(
            [df['Units'] >= 20, df['Units'] >= 10, df['Units'] >= 1],
            ['2 x Diamond', 'Diamond', 'Platinum'],
            default='Gold'
        )
        print("Data extraction complete.")
        return df


    def save_data(self, df):
        print(f"Saving {len(df)} songs to CSV...")
        df.to_csv('All-RIAA-records.csv', index=False)
        print(f'{len(df)} songs saved to All-RIAA-records.csv')

if __name__ == '__main__':
        with WebDriverContextManager() as driver:
            scraper = GoldPlatinumArtistsRIAA(driver)
            data = scraper.fetch_data()
            scraper.save_data(data)