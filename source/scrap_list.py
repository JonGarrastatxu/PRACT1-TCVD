from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from bs4 import BeautifulSoup
import random 
import pandas as pd
import time


import undetected_chromedriver as uc

class SteamChartsScraper:
    def __init__(self):
        print("Initializing scraper...")

        options = webdriver.ChromeOptions() 
        options.headless = False
        # options.add_argument("start-maximized")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1280,1024")
        options.add_argument("--lang=en-US,en")
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        """ options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

        print("Initializing stealth...")
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        self.wait = WebDriverWait(self.driver, 10) """


    def scrap_all_pages_hrefs(self):

        url = "https://steamdb.info/charts/"

        print("Visiting:", url)
        self.driver.get(url)

        all_data = []

        """ # Does table-apps exists???
        exists = self.driver.execute_script("return document.querySelector('#table-apps') !== null;")
        print("Tabla existe:", exists)
        # Does table-apps have rows?
        num_rows = self.driver.execute_script("return document.querySelectorAll('#table-apps tbody tr').length;")
        print("Número de filas:", num_rows) """
     
        while True:
            print("Waiting for wrapper and rows...")

            # Wait for the wrapper table-apps_wrapper to be laoded
            wrapper = self.wait.until(
                EC.presence_of_element_located((By.ID, "table-apps_wrapper"))
            )

            # Wait for the table-apps_wrapper content to be loaded
            self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "#table-apps_wrapper tbody tr")
                )
            )
            print("Wrapper and rows loaded.")

            # Extract hrefs
            page_data = self.scrap_current_page_hrefs()
            all_data.extend(page_data)

            # DO NOT REMOVE OR COMMENT!!! JUST TO LOAD ONLY ONE PAGE FOR TESTING
            break

            try:
                next_button = wrapper.find_element(By.CSS_SELECTOR, "button.dt-paging-button.next") # Look for next button
                if "disabled" in next_button.get_attribute("class"): # If disabled we're on last page so break
                    break
                next_button.click()
            except:
                break
        return all_data

    def scrap_current_page_hrefs(self):
        # Find all table rows from current page
        table = self.driver.find_element(By.ID, "table-apps")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr.app")
        hrefs = []
        for row in rows:
            try:
                # Extract game href to main chart page
                href = row.find_element(By.CSS_SELECTOR, "td a.b").get_attribute("href")
                hrefs.append(href)
            except:
                continue

        # Remove duplicates
        hrefs = list(dict.fromkeys(hrefs))
        return hrefs

    #  TODO(Jon): scrap game data
    def scrap_game_data(self, href):
        """
    Abre la página del juego (href) y extrae los campos:
    'title', 'app_id', 'app_type', 'developer', 'publisher', 'platforms',
    'technologies', 'last_changenumber', 'last_record_update', 'release_date', 'sys_date'
    Devuelve un dict con esos campos o None si falla.
    """
       
        print(f"Scraping game page: {href}")        
        try:
            self.driver.get(href)
        except Exception as e:
            print("Error while openning URL:",e)
            return None
        # Wait till the title loads (h1)
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except Exception:
            print("timeout while waiting for title in", href)
        # Wait to ensure that the JS finishes
        time.sleep(0.6)


        # Get HTML and parse with BeautifulSoup 
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

        # Title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Info Table

        info_table = soup.select_one("tbody")
        info = {}
        if info_table:
            rows = info_table.find_all("tr")
            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    key = tds[0].get_text(strip=True)
                    # For links in td, mantain text
                    value = tds[1].get_text(" ", strip=True)
                    info[key] = value

        # Final dict
        data = {
            "title": title,
            "app_id": info.get("App ID"),
            "app_type": info.get("App Type"),
            "developer": info.get("Developer"),
            "publisher": info.get("Publisher"),
            "platforms": info.get("Supported Systems"),
            "technologies": info.get("Technologies"),
            "last_changenumber": info.get("Last Changenumber"),
            "last_record_update": info.get("Last Record Update"),
            "release_date": info.get("Release Date"),
            "sys_date": datetime.utcnow().isoformat(),
            "href": href

        }
        
        # Avoid server overload
        time.sleep(random.uniform(0.8, 1.6))      

        # Logic to extract game data and rename columns
        # Must return a dict
        return data
    
    # TODO: scrap all games
    def scrap_all_games(scraper, csv_file="steam_hrefs.csv"):
        df_hrefs = pd.read_csv(csv_file)

        # Example columns, WE'GOING TO ADD MORE
        # The rest of columns would come from the chart page subcategories so this list is basic and for example
        # sys_date will be our scrap date using datetime.now()
        columnas = ['title', 'app_id', 'app_type', 'developer', 'publisher', 'platforms', 'technologies', 'last_changenumber', 
                    'last_record_update', 'release_date', 'sys_date'] 
        
        df_results = pd.DataFrame(columns=columnas)

        for i, href in enumerate(df_hrefs['0']):
            print(f"[{i+1}/{len(df_hrefs)}] Scraping {href}...")
            data = scraper.scrap_game_data(href)
            if data:
                df_results = pd.concat([df_results, pd.DataFrame([data])], ignore_index=True)

            break

        return df_results

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
    
    def close(self):
        self.driver.quit()