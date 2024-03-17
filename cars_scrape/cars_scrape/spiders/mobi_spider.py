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
                handle_httpstatus_list=[302, 308]
            ),
            callback=self.parse_page
        )

    async def parse_page(self, response):
        page = respose.meta['playwright_page']
        playwright_page_methods = response.meta['playwright_page_methods']

        possible_classes = [
            response.xpath('//a[@class="mui-style-xsroma"]/@href').getall(),
            response.xpath('//a[@class="css-xsroma"]/@href').getall()
        ] 
        possible_classes = [diff_zero for diff_zero in possible_classes if len(diff_zero) != 0]

        for url in possible_classes[0]:
            yield Request(
                url=url,
                meta = dict(
                    dont_redirect=True,
                    handle_httpstatus_list=[302, 308],
                    playwright=True,
                    playwright_include_page=True,
                    errback=self.errback
                ),
                callback=self.parse_auto_items
            )

    async def parse_auto_items(self, response):
        page = response.meta['playwright_page']

        await page.evaluate(r'''
                             
                            ''')