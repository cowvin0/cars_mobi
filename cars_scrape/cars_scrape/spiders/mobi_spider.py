import scrapy
from scrapy.http import Request
from items import CarsItem


class CarsSpider(scrapy.Spider):
    name = "mobi"
    allowed_domains = ["https://www.mobiauto.com.br"]

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(CarsSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["https://www.mobiauto.com.br/comprar/pb-joao-pessoa"]

    def start_requests(self):
        yield Request(
                url=self.start_requests[0],
                )
