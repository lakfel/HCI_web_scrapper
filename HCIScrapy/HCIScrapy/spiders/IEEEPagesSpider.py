import scrapy


class IeeepagesspiderSpider(scrapy.Spider):
    name = "IEEESpider"
    allowed_domains = ["ieeexplore.ieee.org"]
    start_urls = ["https://ieeexplore.ieee.org"]

    def start_requests(self):
        pass

    def parse(self, response):
        pass
