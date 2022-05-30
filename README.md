# yad2rantalscraper
Rental scraping on yad2 site.

# Usage Example
```
python yad2/main.py --config "path to your config"
```

# Config Example
The config should be a json file which contains the pages you want to scrape and email which should get notifictions</br>
```
{
    "scrape_urls": [
        "https://www.yad2.co.il/realestate/1",
        "https://www.yad2.co.il/realestate/2",
        "https://www.yad2.co.il/realestate/3"
    ],
    "recipients": ["mymail@gmail.com"]
}
```

# Notifications
We're currently using gmail, but it should be blocked around 30/05/2022 - hence we need to find workaround.</br>
Anyway, the username and password should be located under:</br>
```~/.config/gmail.pass```

# Development
Simply create with conda:
```
conda env create --file environment.yml
````

