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
import re


import undetected_chromedriver as uc

class SteamChartsScraper:
    def __init__(self):
        print("Initializing scraper...")

        options = webdriver.ChromeOptions() 
        options.headless = False
        # options.add_argument("start-maximized")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox") # Don't remove unnecessary privileges
        options.add_argument("--disable-gpu") # To use without GPU
        options.add_argument("--disable-dev-shm-usage") # To use without shared memory
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


    def scrap_all_pages_hrefs(self, update):
        """
        Scrap all game hrefs from all dynamic pages.

        Returns:
        list: A list of hrefs of games in all dynamic pages.
        """

        url = "https://steamdb.info/charts/"

        print("Visiting:", url)
        self.driver.get(url)

        if update:
            all_data = pd.read_csv("steam_hrefs.csv")
            all_data = all_data["0"].tolist()
        else:
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
            all_data = self.scrap_current_page_hrefs(all_data)

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


    def scrap_current_page_hrefs(self, all_data):
        
        """
        Scrap all game hrefs from the current page.

        Returns:
        list: A list of hrefs of games in the current page.
        """

        table = self.driver.find_element(By.ID, "table-apps")
        # Find all table rows from current page
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr.app")
        for row in rows:
            try:
                # Extract game href to main chart page
                href = row.find_element(By.CSS_SELECTOR, "td a.b").get_attribute("href")
                if href not in all_data:
                    all_data.append(href)
            except:
                continue
        return all_data


    def scrap_game_data(self, href):
        """
        Scrap game data from a given href.
        
        Parameters:
        href (str): href of the game page to scrape.
        
        Returns:
        dict: A dictionary containing the scraped data with the following keys:
            - title (str): The title of the game.
            - app_id (int): The app ID of the game.
            - app_type (str): The app type of the game.
            - developer (str): The developer of the game.
            - publisher (str): The publisher of the game.
            - platforms (str): The supported systems of the game.
            - technologies (str): The technologies used in the game.
            - last_changenumber (str): The last changenumber of the game.
            - last_record_update (str): The last record update of the game.
            - release_date (str): The release date of the game.
            - positive_reviews_per (float): The percentage of positive reviews of the game.
            - total_reviews (int): The total number of reviews of the game.
            - player_count_now (int): The number of players currently playing the game.
            - sys_date (datetime): The date when the data was scraped.
            - href (str): The href of the game page that was scraped.
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

        # Get HTML and parse with BeautifulSoup (Better to not interact in real time with the page)
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

        # Title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        ############################################################################
        # Main Info Table
        ############################################################################
        info_table = soup.select_one("table.table.table-bordered.table-responsive-flex tbody")
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

        ############################################################################
        # Positive reviews percentage and player count right now
        ############################################################################
        header_block = soup.select_one("div.header-two-things")
        if header_block:
            reviews_link = header_block.select_one("a#js-reviews-button")
            if reviews_link:
                aria_label = reviews_link.get("aria-label", "")
                
                # Search positive reviews percentage (ej. 86.39%)
                match_perc = re.search(r"(\d{1,3}\.\d{2})%", aria_label)
                if match_perc:
                    info["positive_reviews_per"] = float(match_perc.group(1))
                else:
                    info["positive_reviews_per"] = None
                
                # Search total review count (ej. of the 9,104,053)
                match_total = re.search(r"of the ([\d,]+)", aria_label)
                if match_total:
                    total_reviews_str = match_total.group(1).replace(",", "")
                    info["total_reviews"] = int(total_reviews_str)
                else:
                    info["total_reviews"] = None

            # Search player count
            charts_link = header_block.select_one("a#js-charts-button .header-thing-number")
            if charts_link:
                player_count_str = charts_link.get_text(strip=True).replace(",", "")
                info["player_count_now"] = int(player_count_str)
            else:
                info["player_count_now"] = None

        ############################################################################
        # Categories
        ############################################################################
        categories_block = soup.select_one("div.header-thing.header-thing-categories")
        categories = {}

        # Categories to use
        categories_to_use = [
            "Multi-player",
            "Steam Trading Cards",
            "Valve Anti-Cheat",
            "In-App Purchases",
            "Steam Workshop",
            "Cloud Gaming",
            "Cross-Platform Multiplayer",
            "Stats",
            "Remote Play on Phone",
            "Remote Play on Tablet"
        ]

        if categories_block:
            # Search all <a> with attribute aria-label (los nombres de categoría)
            category_links = categories_block.find_all("a", attrs={"aria-label": True})
            
            for link in category_links:
                label = link["aria-label"].strip()
                if label in categories_to_use:
                    categories[label] = 1

        # If category not found, set it to 0
        for cat in categories_to_use:
            if cat not in categories:
                categories[cat] = 0

        ############################################################################
        # Main dict
        data = {
            # General
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
            "positive_reviews_per": info.get("positive_reviews_per"),
            # Reviews
            "total_reviews": info.get("total_reviews"),
            "player_count_now": info.get("player_count_now"),
            # Categories
            "multiplayer": categories.get("Multi-player"),
            "steam_trading_cards": categories.get("Steam Trading Cards"),
            "valve_anti_cheat": categories.get("Valve Anti-Cheat"),
            "in_app_purchases": categories.get("In-App Purchases"),
            "steam_workshop": categories.get("Steam Workshop"),
            "cloud_gaming": categories.get("Cloud Gaming"),
            "cross_platform_multiplayer": categories.get("Cross-Platform Multiplayer"),
            "stats": categories.get("Stats"),
            "remote_play_on_phone": categories.get("Remote Play on Phone"),
            "remote_play_on_tablet": categories.get("Remote Play on Tablet"),
            # Scrap info
            "sys_date": datetime.utcnow().isoformat(),
            "href": href
        }
        
        # Avoid server overload
        time.sleep(random.uniform(0.8, 1.6))      

        # Logic to extract game data and rename columns
        # Must return a dict
        return data
    
    # TODO: scrap all games
    def scrap_all_games(scraper, update, csv_file="steam_hrefs.csv"):
        """
        Scrap all games from the given CSV file and return a DataFrame with the desired columns.

        Parameters:
        scraper (SteamChartsScraper): The scraper object to use for scraping.
        csv_file (str): The path to the CSV file containing the game hrefs to scrape.

        Returns:
        pd.DataFrame: A DataFrame containing the scraped game data with the desired columns.
        """

        df_hrefs = pd.read_csv(csv_file)

        # sys_date will be our scrap date using datetime.now()
        columnas = [
        'title', 'app_id', 'app_type', 'developer', 'publisher', 'platforms',
        'technologies', 'last_changenumber', 'last_record_update', 'release_date', 
        'positive_reviews_per', 'total_reviews', 'player_count_now', 'multiplayer',
        'steam_trading_cards', 'valve_anti_cheat', 'in_app_purchases', 'steam_workshop', 
        'cloud_gaming', 'cross_platform_multiplayer', 'stats', 'remote_play_on_phone', 
        'remote_play_on_tablet', 'sys_date', 'href'
        ]

        dtypes = {
            # General
            'title': 'string',
            'app_id': 'Int64',
            'app_type': 'string',
            'developer': 'string',
            'publisher': 'string',
            'platforms': 'string',
            'technologies': 'string',
            'last_changenumber': 'string',
            'last_record_update': 'string',
            'release_date': 'string',
            'positive_reviews_per': 'float64',
            'total_reviews': 'Int64',
            # Categories
            'multiplayer': 'Int64',
            'steam_trading_cards': 'Int64',
            'valve_anti_cheat': 'Int64',
            'in_app_purchases': 'Int64',
            'steam_workshop': 'Int64',
            'cloud_gaming': 'Int64',
            'cross_platform_multiplayer': 'Int64',
            'stats': 'Int64',
            'remote_play_on_phone': 'Int64',
            'remote_play_on_tablet': 'Int64',
            # Scrap info
            'player_count_now': 'Int64',
            'sys_date': 'datetime64[ns]'
        }

        if update:
            df_results = pd.read_csv(
                "dataset/steam_dataset.csv",
                dtype={k: v for k, v in dtypes.items() if v != "datetime64[ns]"},
                parse_dates=[k for k, v in dtypes.items() if v == "datetime64[ns]"]
        )
        else:
            df_results = pd.DataFrame(columns=columnas).astype(dtypes)

        for i, href in enumerate(df_hrefs['0']):
            print(f"[{i+1}/{len(df_hrefs)}] Scraping {href}...")
            data = scraper.scrap_game_data(href)
            if data:
                df_results = pd.concat([df_results, pd.DataFrame([data])], ignore_index=True)

            break # DO NOT REMOVE OR COMMENT!!! JUST TO LOAD ONLY ONE PAGE FOR TESTING

        return df_results

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
    
    def close(self):
        self.driver.quit()