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
            url=self.start_urls[0],
            meta=dict(
                dont_redirect=True,
                handle_httpstatus_list=[302, 308],
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods={
                    ...
                    },
                errback=self.errback
            ),
            callback=self.parse
        )
