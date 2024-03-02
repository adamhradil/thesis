from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider
from scrapy import signals


items = []

def item_scraped(item, response, spider):
    items.append(item)

process = CrawlerProcess()
crawler = process.create_crawler(SrealitySpider)
crawler.signals.connect(item_scraped, signal=signals.item_scraped)
crawler2 = process.create_crawler(SearchFlatsSpider)
crawler2.signals.connect(item_scraped, signal=signals.item_scraped)
process.crawl(crawler)
process.crawl(crawler2)
process.start()

print("test")
