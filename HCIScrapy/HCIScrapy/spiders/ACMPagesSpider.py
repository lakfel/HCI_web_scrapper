import scrapy


class AcmspiderSpider(scrapy.Spider):
    name = "ACMSpider"
    allowed_domains = ["dl.acm.org"]
    start_urls = ["https://dl.acm.org"]

    def parse(self, response):
        pass
