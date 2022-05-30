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

# Development
Simply create with conda:
```
conda env create --file yad2/environment.yml
````
