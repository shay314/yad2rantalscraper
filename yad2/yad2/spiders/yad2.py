import logging
import random
import re
import time
import copy
from typing import Dict, List

import boto3
import dominate
import scrapy
from bs4 import BeautifulSoup
from tabulate import tabulate

from yad2.spiders.email import Mail

URLS_TO_SCAPRE_FROM = [
    "https://www.yad2.co.il/realestate/rent?topArea=2&area=8&city=1200&rooms=3-5&price=-1-6500&EnterDate=1657832400--1&comment=%D7%90%D7%91%D7%A0%D7%99%20%D7%97%D7%9F",
    "https://www.yad2.co.il/realestate/rent?topArea=2&area=8&city=1200&rooms=3-5&price=-1-6500&EnterDate=1657832400--1&comment=%D7%94%D7%9E%D7%92%D7%99%D7%A0%D7%99%D7%9D",
    "https://www.yad2.co.il/realestate/rent?topArea=2&area=8&city=1200&rooms=3-5&price=-1-6500&EnterDate=1657832400--1&comment=%D7%94%D7%9B%D7%A8%D7%9E%D7%99%D7%9D",
]
TABLE_HEADERS = ["Index", "Title", "Rooms", "Floor", "Price"]

import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logging.info("Admin logged in")


class Yad2Item(scrapy.Item):
    title = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    price = scrapy.Field()


class Yad2Spider(scrapy.Spider):
    name = "yad2_spider"
    allowed_domains = ["yad2.co.il"]

    start_url = URLS_TO_SCAPRE_FROM[0]
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/72.0.3626.119 Safari/537.36"
    }

    mail = Mail()

    def __init__(self, *args, **kwargs):
        super(Yad2Spider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs
        )
        self.prev_results = set([])
        self.curren_results = []
        self.scrape_index = 0

    def start_requests(self):
        yield scrapy.Request(
            self.start_url, callback=self.parse_search_url, headers=self.HEADERS
        )

    def parse_search_url(self, response):
        # extract results
        soup = BeautifulSoup(response.body, "html.parser")
        feed_list = soup.find_all("div", class_="feed_list")
        if len(feed_list) > 0:
            feed_list = feed_list[0]

            houses = feed_list.find_all(
                "div", class_="feed_item", id=re.compile("^feed_item")
            )

            self.curren_results += [self.parse_house(house) for house in houses]
        else:
            logging.warning("did not found any housing")

        # examine results
        done_scraping_round = self.scrape_index == len(URLS_TO_SCAPRE_FROM) - 1
        if done_scraping_round:
            self.examine_and_notify()

        # rescrape
        self.scrape_index = (self.scrape_index + 1) % len(URLS_TO_SCAPRE_FROM)
        logging.info("new url index %d", self.scrape_index)
        next_url = URLS_TO_SCAPRE_FROM[self.scrape_index]
        yield scrapy.Request(
            next_url,
            callback=self.parse_search_url,
            headers=self.HEADERS,
            dont_filter=True,
        )

    def examine_and_notify(self):
        # check if we need to notify the user
        new_houses_set = set([r["title"] for r in self.curren_results])
        # change_from_last_test = new_houses_set.symmetric_difference(self.prev_results)
        change_from_last_test = new_houses_set.difference(self.prev_results)

        if (
            len(self.prev_results) > 0
            and len(new_houses_set) > 0
            and len(change_from_last_test) > 0
        ):
            logging.info("found diff %s", change_from_last_test)
            logging.info("prev %s:", self.prev_results)
            logging.info("new %s:", new_houses_set)
            self.notify(self.curren_results)

        self.prev_results = copy.deepcopy(new_houses_set)
        self.curren_results = []

        # sleep a bit
        sleep_time_seconds = random.randint(60 * 20, 60 * 30)
        logging.info("sleeping for %d minutes", int(sleep_time_seconds / 60.0))
        time.sleep(sleep_time_seconds)

    def parse_house(self, house):
        item = Yad2Item()

        item["title"] = house.find_all("span", class_="title")[0].text.strip()
        item["rooms"] = float(
            house.find_all("span", id=re.compile("^data_room"))[0].text
        )
        item["floor"] = house.find_all("span", id=re.compile("^data_floor"))[0].text

        price = (
            house.find_all("div", class_=re.compile("^price"))[0]
            .text.strip()
            .split()[0]
        )
        item["price"] = int(price.replace(",", ""))

        return item

    def notify(self, results: List[Yad2Item]):
        logging.info("found changes in the status")
        display(results)
        # content = convert_to_html(results)
        msg = f"connect to yad 2!"
        self.mail.send(["shay.mrglit@gmail.com"], "Found change in housing!", msg)

    def convert_to_html(self, results) -> str:
        doc = dominate.document(title="Change in rant housing")

        with doc.head:
            dominate.tags.link(rel="stylesheet", href="style.css")

        with doc:
            # define table style
            dominate.tags.style("table{border-collapse:collapse}")
            dominate.tags.style(
                "th{font-size:small;border:1px solid gray;padding:4px;background-color:#DDD}"
            )
            dominate.tags.style(
                "td{font-size:small;text-align:center;border:1px solid gray;padding:4px}"
            )
            dominate.tags.h1("A change in housing was discovered")
            dominate.tags.p("We discovered a change in the housing situtation")

            table = [
                (i + 1, h["title"], h["rooms"], h["floor"], h["price"])
                for i, h in enumerate(results)
            ]
            create_table(table_headers=TABLE_HEADERS, data=table)
            dominate.tags.a(
                "see the change in this link",
                href=URLS_TO_SCAPRE_FROM[self.scrape_index],
            )

        return str(doc)


def create_table(table_headers, data):
    """creating html table for the given data

    :param str table_headers: the table headers
    :param pd.DataFrame data: table data
    """
    with dominate.tags.table(border=1):
        # write table headers
        with dominate.tags.thead():
            for header in table_headers:
                dominate.tags.th(header, style="color:white;background-color:gray")

        # write table body
        with dominate.tags.tbody():
            for row_data in data:
                with dominate.tags.tr():
                    for value in row_data:
                        dominate.tags.td(value)


def display(results: List[Dict]):
    table = [
        (i + 1, h["title"], h["rooms"], h["floor"], h["price"])
        for i, h in enumerate(results)
    ]
    print(
        tabulate(table, headers=TABLE_HEADERS),
    )
