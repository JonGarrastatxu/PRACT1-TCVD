from scrap_list import SteamChartsScraper
import argparse


def main(args):
    # Initialize scraper
    scraper = SteamChartsScraper()
    
    # Scrape hrefs of all games in all dynamic pages
    if not args.skip:
        data = scraper.scrap_all_pages_hrefs(args.update)
        scraper.save_to_csv(data, "steam_hrefs.csv")

    # TODO: Scrape games from steam_hrefs.csv
    # Limited to one for testing
    data_pd = scraper.scrap_all_games(args.update)

    # Save dataset
    data_pd.to_csv("dataset/steam_dataset.csv", index=False)
    
    # Close scraper
    scraper.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper de Steam Charts")

    # Skip hrefs scraping
    parser.add_argument(
        "--skip", 
        action="store_true",
        help="Skip hrefs scraping (Use steam_hrefs.csv)")
    
    # If update is false, this is equivalent to OVERWRITE ALL!!!
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing hrefs instead of starting from scratch")
    
    args = parser.parse_args()
    main(args)
