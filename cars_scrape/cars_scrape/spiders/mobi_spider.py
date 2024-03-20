import scrapy
from scrapy.http import Request
# from items import CarsItem


class CarsSpider(scrapy.Spider):
    name = "mobi"
    allowed_domains = ["www.mobiauto.com.br"]

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(CarsSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["https://www.mobiauto.com.br/comprar/carros/pb-joao-pessoa"]

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            meta=dict(
                dont_redirect=True,
                handle_httpstatus_list=[302, 308, 307]
            ),
            callback=self.parse_page
        )

    async def parse_page(self, response):
        # page = response.meta['playwright_page']
        # playwright_page_methods = response.meta['playwright_page_methods']

        possible_classes = [
            response.xpath('//a[@class="mui-style-xsroma"]/@href').getall(),
            response.xpath('//a[@class="css-xsroma"]/@href').getall()
            ] 

        possible_classes = [diff_zero for diff_zero in possible_classes if len(diff_zero) != 0]

        for url in possible_classes[0]:
            yield Request(
                url="https://www.mobiauto.com.br" + url,
                meta = dict(
                    dont_redirect=True,
                    handle_httpstatus_list=[302, 308, 307],
                    playwright=True,
                    playwright_include_page=True,
                    errback=self.errback
                ),
                callback=self.parse_auto_items
            )

    async def parse_auto_items(self, response):
        page = response.meta['playwright_page']

        await page.evaluate(r'''
                            var elements = document.querySelectorAll('.MuiAccordionSummary-content.MuiAccordionSummary-contentGutters.css-17o5nyn, .MuiAccordionSummary-content.MuiAccordionSummary-contentGutters.mui-style-17o5nyn');
                            Array.from(elements).forEach(element => element.click());
                            ''')

        await page.wait_for_timeout(5000)

        car_details = await page.evaluate(r'''
                                          var details = document.querySelectorAll(".MuiCollapse-wrapperInner.MuiCollapse-vertical.mui-style-8atqhb");
                                          Array.from(details).forEach(element => element.textContent);
                                          ''')

        yield {"items": car_details}