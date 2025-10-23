from scrap_list import SteamChartsScraper

def main():
    # Initialize scraper
    scraper = SteamChartsScraper()
    
    # Scrape hrefs of all games in all dynamic pages
    data = scraper.scrap_all_pages_hrefs()
    scraper.save_to_csv(data, "steam_hrefs.csv")

    # TODO: Scrape games from steam_hrefs.csv
    # Limited to one for testing
    data_pd = scraper.scrap_all_games()

    # TODO: Save dataset
    data_pd.to_csv("steam_dataset.csv", index=False)
    
    # Close scraper
    scraper.close()

if __name__ == "__main__":
    main()
