import argparse

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from yad2.spiders.yad2 import Yad2Spider


def get_arg_parser():
    """parse arguments"""
    parser = argparse.ArgumentParser(description="scarp yad2 for rantal info")
    parser.add_argument("--config", help="full path to configuration file", type=str, required=True)
    return parser.parse_args()


def main():
    """main method"""
    parser = get_arg_parser()
    settings = get_project_settings()

    # for [trying to] prevent bendding
    # https://docs.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned
    settings["COOKIES_ENABLED"] = False
    settings["DOWNLOAD_DELAY"] = 3
    runner = CrawlerRunner(settings=settings)
    runner.crawl(Yad2Spider, parser.config)
    deferred = runner.join()
    deferred.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    main()
