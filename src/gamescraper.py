import requests

print(requests.get("https://store.steampowered.com/app/10").text)


#filters = "supported_languages,fullgame,developers,demos,price_overview,metacritic,categories,controller_support,genres,recommendations,achievements"

#languages- class: game_language_options
#categories- class: app_tag
#developers- class: dev_row
#price_overview- class: discount_prices CHECK
#genre- id: genresAndManufacturer
#metacrtic- class: score high
#recommendations: 