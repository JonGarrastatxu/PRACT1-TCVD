from scrap_list import SteamChartsScraper

def main():
    # Initialize scraper
    scraper = SteamChartsScraper()
    
    # Scrape hrefs of all games in all dynamic pages
    data = scraper.scrap_all_pages_hrefs()
    scraper.save_to_csv(data, "steam_hrefs.csv")
    
    
    if len(data) > 0:
       first_href = data[0]
       print(f"\n🔍 Probando scrap_game_data con el primer href:\n{first_href}\n")
       game_data = scraper.scrap_game_data(first_href)
       print("Resultado del scraping del primer juego:")
       print(game_data)
    else:
       print("⚠️ No se obtuvieron hrefs, revisa si la tabla se cargó correctamente.")

    # TODO: Scrape games from steam_hrefs.csv
    data_pd = scraper.scrap_all_games()

    # TODO: Save dataset
    data_pd.to_csv("steam_dataset.csv", index=False)
    
    # Close scraper
    scraper.close()

if __name__ == "__main__":
    main()
